"""Souvislá Vlasta: jeden požadavek na odstavec, přesná metadata, původní titulky."""

import argparse
import asyncio
import hashlib
import html
import json
import re
import sys
import textwrap
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from prepare_spoken_text import LEXICON, prepare  # noqa: E402


def projected_words(display, spoken, replacements, boundaries):
    """Promítne fonetické tokeny služby na původní pravopis bez změny obsahu."""
    changes, shift = [], 0
    for item in replacements:
        start = item["start"] + shift
        end = start + len(item["spoken"])
        changes.append((start, end, item["start"], item["end"]))
        shift += len(item["spoken"]) - (item["end"] - item["start"])

    def project(start, end):
        overlaps = [c for c in changes if start < c[1] and end > c[0]]
        if overlaps:
            return min(c[2] for c in overlaps), max(c[3] for c in overlaps)
        delta = sum((c[1] - c[0]) - (c[3] - c[2]) for c in changes if c[1] <= start)
        return start - delta, end - delta

    words, cursor = [], 0
    for boundary in boundaries:
        word = html.unescape(boundary["text"])
        start = spoken.find(word, cursor)
        if start < 0:
            # Povolena pouze case varianta stejného textu, nikoli odhad časů.
            start = spoken.casefold().find(word.casefold(), cursor)
        if start < 0:
            raise ValueError(f"Boundary se neshoduje s řečovým vstupem: {word!r}")
        if any(char.isalnum() for char in spoken[cursor:start]):
            raise ValueError("Word boundaries vynechaly část řečového vstupu.")
        end = start + len(word)
        cursor = end
        left, right = project(start, end)
        event = {
            "left": left,
            "right": right,
            "start": boundary["offset"] / 10_000_000,
            "end": (boundary["offset"] + boundary["duration"]) / 10_000_000,
        }
        if event["end"] < event["start"] or (words and event["start"] < words[-1]["start"]):
            raise ValueError("Word boundaries nemají platné pořadí časů.")
        if words and left <= words[-1]["left"] and right == words[-1]["right"]:
            words[-1]["end"] = event["end"]
        else:
            words.append(event)
    if not words:
        raise ValueError("Služba nevrátila word boundary metadata.")
    if any(char.isalnum() for char in spoken[cursor:]):
        raise ValueError("Word boundaries nepokrývají konec řečového vstupu.")
    cues, group, original_cursor = [], [], 0
    for word in words:
        if (
            group
            and word["left"] > 0
            and display[word["left"] - 1].isspace()
            and (word["right"] - original_cursor > 82 or word["end"] - group[0]["start"] > 6.5)
        ):
            cut = word["left"]
            cues.append(
                {
                    "start": group[0]["start"],
                    "end": group[-1]["end"],
                    "text": display[original_cursor:cut].strip(),
                }
            )
            original_cursor = cut
            group = []
        group.append(word)
    if group:
        cues.append(
            {
                "start": group[0]["start"],
                "end": group[-1]["end"],
                "text": display[original_cursor:].strip(),
            }
        )
    combined = " ".join(c["text"] for c in cues)

    def normalize(text):
        return re.sub(r"\s+", " ", text).strip()

    if normalize(combined) != normalize(display):
        raise ValueError("Titulky nezachovaly přesný původní text.")
    return cues


def timestamp(seconds, comma=False):
    value = max(0, round(seconds * 1000))
    hours, value = divmod(value, 3_600_000)
    minutes, value = divmod(value, 60_000)
    secs, millis = divmod(value, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}{',' if comma else '.'}{millis:03}"


def write_captions(cues, target):
    srt, vtt = [], ["WEBVTT\n"]
    for number, cue in enumerate(cues, 1):
        lines = "\n".join(
            textwrap.wrap(cue["text"], width=43, break_long_words=False, break_on_hyphens=False)
        )
        srt.append(
            f"{number}\n{timestamp(cue['start'], True)} --> "
            f"{timestamp(cue['end'], True)}\n{lines}\n"
        )
        vtt.append(f"{timestamp(cue['start'])} --> {timestamp(cue['end'])}\n{lines}\n")
    target.with_suffix(".srt").write_text("\n".join(srt), encoding="utf-8")
    target.with_suffix(".vtt").write_text("\n".join(vtt), encoding="utf-8")


async def synthesize_scene(scene, directory, lexicon):
    display = scene["paragraph"]
    spoken, changes = prepare(display, lexicon)
    signature = hashlib.sha256(
        json.dumps(
            {
                "display": display,
                "spoken": spoken,
                "voice": "cs-CZ-VlastaNeural",
                "rate": "-3%",
                "boundary": "WordBoundary",
            },
            ensure_ascii=False,
            sort_keys=True,
        ).encode()
    ).hexdigest()
    target = directory / f"{scene['id']}_{signature[:12]}.mp3"
    sidecar = target.with_suffix(".json")
    if target.is_file() and sidecar.is_file():
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        if (
            data.get("signature") == signature
            and data.get("audio_sha256") == hashlib.sha256(target.read_bytes()).hexdigest()
        ):
            data["cues"] = projected_words(display, spoken, changes, data["word_boundaries"])
            data["captions_algorithm"] = 2
            sidecar.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            write_captions(data["cues"], target)
            return data
    boundaries = []
    partial = target.with_suffix(".part")
    raw_path = target.with_suffix(".boundaries.json")
    previous = json.loads(raw_path.read_text(encoding="utf-8")) if raw_path.exists() else None
    recoverable = (
        previous
        and previous.get("spoken") == spoken
        and partial.exists()
        and previous.get("audio_sha256") == hashlib.sha256(partial.read_bytes()).hexdigest()
    )
    speech = edge_tts.Communicate(
        spoken,
        "cs-CZ-VlastaNeural",
        rate="-3%",
        boundary="WordBoundary",
        connect_timeout=15,
        receive_timeout=45,
    )
    if recoverable:
        boundaries = previous["boundaries"]
    else:
        with partial.open("wb") as audio:
            async for event in speech.stream():
                if event["type"] == "audio":
                    audio.write(event["data"])
                elif event["type"] == "WordBoundary":
                    boundaries.append({key: event[key] for key in ("text", "offset", "duration")})
    if partial.stat().st_size < 1000:
        raise ValueError("Audio je prázdné nebo neúplné.")
    raw = {
        "display": display,
        "spoken": spoken,
        "replacements": changes,
        "boundaries": boundaries,
        "audio_sha256": hashlib.sha256(partial.read_bytes()).hexdigest(),
    }
    raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    cues = projected_words(display, spoken, changes, boundaries)
    partial.replace(target)
    data = {
        "id": scene["id"],
        "signature": signature,
        "voice": "cs-CZ-VlastaNeural",
        "unit": "continuous_paragraph",
        "display_text": display,
        "spoken_text": spoken,
        "replacements": changes,
        "word_boundaries": boundaries,
        "cues": cues,
        "audio": str(target.relative_to(ROOT)),
        "audio_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "human_listening_review": "not_claimed",
        "captions_algorithm": 2,
    }
    sidecar.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_captions(cues, target)
    return data


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--plan", type=Path, default=ROOT / "video_course/storyboard/course_plan.json"
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--start", default="01_00")
    parser.add_argument("--scenes", nargs="+", help="Obnovit jen výslovně vybrané scény.")
    parser.add_argument("--cache-only", action="store_true")
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    lexicon = json.loads(LEXICON.read_text(encoding="utf-8"))
    directory = ROOT / "video_course/narration/vlasta"
    directory.mkdir(parents=True, exist_ok=True)
    selected = [scene for scene in plan if scene["id"] >= args.start]
    if args.scenes:
        if set(args.scenes) - {scene["id"] for scene in plan}:
            raise ValueError("Neznámá scéna pro obnovu komentáře.")
        selected = [scene for scene in selected if scene["id"] in args.scenes]
    selected = selected[: args.limit] if args.limit else selected
    for number, scene in enumerate(selected, 1):
        data = await asyncio.wait_for(synthesize_scene(scene, directory, lexicon), timeout=180)
        scene["audio"] = data["audio"]
        scene["cues"] = data["cues"]
        scene["voice"] = data["voice"]
        if not args.cache_only:
            args.plan.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        status = {
            "completed": number,
            "selected": len(selected),
            "scene": scene["id"],
            "voice": data["voice"],
            "unit": data["unit"],
        }
        name = f"speech-progress-{args.start}.json" if args.cache_only else "speech-progress.json"
        (ROOT / "evidence" / name).write_text(json.dumps(status), encoding="utf-8")
        print(json.dumps(status), flush=True)
        await asyncio.sleep(3)  # Nízká frekvence požadavků, žádné obcházení omezení služby.


if __name__ == "__main__":
    asyncio.run(main())
