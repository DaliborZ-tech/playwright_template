"""Freeze an isolated Git snapshot and build only the R2 reference narration."""

import asyncio
import hashlib
import json
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "video_course/production"))
import studio  # noqa: E402
from continuous_speech import synthesize_scene, write_captions  # noqa: E402
from prepare_spoken_text import prepare  # noqa: E402


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def freeze():
    reference = json.loads(
        (ROOT / "video_course/reference_manifest.json").read_text(encoding="utf-8")
    )
    snapshot = ROOT / ".tools/r2-starter-snapshot"
    if not (snapshot / ".git").exists():
        snapshot.mkdir(parents=True, exist_ok=True)
        for name, digest in reference["sha256"].items():
            assert sha(ROOT / name) == digest, name
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        subprocess.run(
            ["git", "init", "--initial-branch=r2-frozen"],
            cwd=snapshot,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "-c", "core.autocrlf=false", "add", "--all"], cwd=snapshot, check=True
        )
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Playwright Academy",
                "-c",
                "user.email=academy@example.test",
                "commit",
                "-m",
                "Freeze verified Starter Kit for R2 reference chapter",
            ],
            cwd=snapshot,
            check=True,
            capture_output=True,
        )
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=snapshot, text=True).strip()
    for name, digest in reference["sha256"].items():
        blob = subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=snapshot)
        assert hashlib.sha256(blob).hexdigest() == digest, name
    bundle = HERE / "starter-reference.bundle"
    if bundle.exists():
        bundle.unlink()
    subprocess.run(["git", "bundle", "create", str(bundle), "r2-frozen"], cwd=snapshot, check=True)
    data = {
        "commit": commit,
        "bundle": bundle.name,
        "bundle_sha256": sha(bundle),
        "source_manifest": reference,
        "main_worktree_index_modified": False,
        "test_command": ".venv/Scripts/python.exe -m pytest tests training/solutions",
        "environment": "Windows11 x64 / Python3.12.15 / locked Chromium",
        "manual_version": "The exact training files are included in this commit",
    }
    (HERE / "reference.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return data


def word_map(display, spoken, changes, boundaries):
    spans, shift = [], 0
    for change in changes:
        start = change["start"] + shift
        end = start + len(change["spoken"])
        spans.append((start, end, change["start"], change["end"]))
        shift += len(change["spoken"]) - (change["end"] - change["start"])
    cursor, words = 0, []
    for boundary in boundaries:
        import html

        token = html.unescape(boundary["text"])
        start = spoken.casefold().find(token.casefold(), cursor)
        if start < 0 or any(c.isalnum() for c in spoken[cursor:start]):
            raise ValueError("Incomplete native speech boundaries")
        end = start + len(token)
        overlaps = [s for s in spans if start < s[1] and end > s[0]]
        if overlaps:
            left, right = min(s[2] for s in overlaps), max(s[3] for s in overlaps)
        else:
            delta = sum((s[1] - s[0]) - (s[3] - s[2]) for s in spans if s[1] <= start)
            left, right = start - delta, end - delta
        current = {
            "left": left,
            "right": right,
            "start": boundary["offset"] / 1e7,
            "end": (boundary["offset"] + boundary["duration"]) / 1e7,
        }
        if words and words[-1]["left"] == left and words[-1]["right"] == right:
            words[-1]["end"] = current["end"]
        else:
            words.append(current)
        cursor = end
    if any(c.isalnum() for c in spoken[cursor:]):
        raise ValueError("Missing end of narration")
    return words


def semantic_captions(text, words):
    cues, group, left = [], [], 0
    for index, word in enumerate(words):
        group.append(word)
        next_left = words[index + 1]["left"] if index + 1 < len(words) else len(text)
        fragment = text[left:next_left].strip()
        sentence_end = bool(re.search(r"[.!?;:]$", fragment))
        clause_end = fragment.endswith(",") and len(fragment) >= 40
        too_long = len(fragment) >= 78 or word["end"] - group[0]["start"] >= 6.5
        if sentence_end or clause_end or too_long or index == len(words) - 1:
            cues.append({"start": group[0]["start"], "end": word["end"], "text": fragment})
            group, left = [], next_left
    assert " ".join(" ".join(c["text"].split()) for c in cues) == " ".join(text.split())
    return cues


async def main():
    freeze()
    plan = json.loads((HERE / "plan.json").read_text(encoding="utf-8"))
    lexicon = json.loads(
        (ROOT / "video_course/production/pronunciation_vlasta.json").read_text(encoding="utf-8")
    )
    lexicon["aliases"].update(
        {
            "test_video_created.py": "test vidijou krijejtyd tečka paj",
            "page.goto": "pejdž gou tu",
            "Page": "pejdž",
            "heading": "hedink",
            "exact": "igzakt",
            "button": "batn",
            "HTML": "há té em el",
            "CSS": "sí es es",
            "h1": "há jedna",
            "h2": "há dva",
            "xfail": "eks fejl",
            "tests": "tests",
            "examples": "igzámpls",
        }
    )
    (HERE / "pronunciation.json").write_text(
        json.dumps(lexicon, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    audio = HERE / "narration"
    audio.mkdir(exist_ok=True)
    offset, all_cues, shots, pcm_frames = 0, [], [], []
    for section in plan["sections"]:
        data = await synthesize_scene(section, audio, lexicon)
        spoken, changes = prepare(section["paragraph"], lexicon)
        words = word_map(section["paragraph"], spoken, changes, data["word_boundaries"])
        cues = semantic_captions(section["paragraph"], words)
        data["cues"] = cues
        data["captions_algorithm"] = "R2_sentence_and_clause_boundaries"
        source = ROOT / data["audio"]
        source.with_suffix(".json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        write_captions(cues, source)
        wav = source.with_suffix(".wav")
        subprocess.run(
            [
                studio.ffmpeg(),
                "-y",
                "-v",
                "error",
                "-i",
                str(source),
                "-ac",
                "1",
                "-ar",
                "48000",
                "-c:a",
                "pcm_s16le",
                str(wav),
            ],
            check=True,
        )
        with wave.open(str(wav)) as stream:
            frames = stream.readframes(stream.getnframes())
        duration = len(frames) / 96000
        pcm_frames.append(frames)
        section.update(
            audio=data["audio"], start=offset, duration=duration, audio_sha256=sha(source)
        )
        section_shots = section["shots"]
        for index, shot in enumerate(section_shots):
            position = section["paragraph"].index(shot["voice_cue"])
            at = next(w["start"] for w in words if w["left"] <= position < w["right"])
            shot.update(
                voice_at=offset + at,
                start=offset if index == 0 else offset + at,
                section=section["id"],
                section_title=section["title"],
            )
            shots.append(shot)
        all_cues.extend({**c, "start": c["start"] + offset, "end": c["end"] + offset} for c in cues)
        offset += duration
        print(
            json.dumps(
                {
                    "section": section["id"],
                    "seconds": duration,
                    "words": len(section["paragraph"].split()),
                }
            ),
            flush=True,
        )
        await asyncio.sleep(2)
    if not 300 <= offset <= 480:
        raise ValueError(f"Reference chapter must be5–8minutes, actual{offset:.2f}s")
    for index, shot in enumerate(shots):
        shot["start"] = round(shot["start"] * 25) / 25
        end = shots[index + 1]["start"] if index + 1 < len(shots) else offset
        shot["end"] = round(end * 25) / 25
        shot["duration"] = round(shot["end"] - shot["start"], 3)
        shot["action_offset"] = max(0, shot["voice_at"] - shot["start"])
    (HERE / "narration.wav").parent.mkdir(exist_ok=True)
    with wave.open(str(HERE / "narration.wav"), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(48000)
        for frames in pcm_frames:
            stream.writeframes(frames)
    plan.update(duration=offset, shots=shots, caption_cues=len(all_cues))
    (HERE / "timeline.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_captions(all_cues, HERE / "subtitles_cs")
    (HERE / "transcript_cs.md").write_text(
        "\n\n".join(f"## {s['title']}\n\n{s['paragraph']}" for s in plan["sections"]),
        encoding="utf-8",
    )
    print(
        json.dumps({"duration": offset, "shots": len(shots), "captions": len(all_cues)}), flush=True
    )


if __name__ == "__main__":
    asyncio.run(main())
