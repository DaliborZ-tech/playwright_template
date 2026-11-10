"""Sestaví skutečné záběry, původní titulky a kapitoly; odmítne neúplný kurz."""
# ruff: noqa: E501 -- Řádky ASS stylů jsou formát dat, nikoli odstavce kódu.

import argparse
import hashlib
import json
import re
import site
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
site.addsitedir(str(ROOT / ".tools/media-env/Lib/site-packages"))
sys.path.insert(0, str(ROOT / "scripts"))

import imageio_ffmpeg  # noqa: E402
from continuous_speech import projected_words, timestamp, write_captions  # noqa: E402
from freeze_reference import current  # noqa: E402
from prepare_spoken_text import LEXICON, prepare  # noqa: E402

TITLE = "Playwright Academy · Python · český kurz"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def probe(path):
    result = subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
    if not match:
        raise ValueError(f"Nečitelná délka: {path.name}")
    hours, minutes, seconds = map(float, match.groups())
    return hours * 3600 + minutes * 60 + seconds, result.stderr


def collect(plan):
    source = current()
    if source != read(ROOT / "video_course/reference_manifest.json")["sha256"]:
        raise ValueError("Zdrojový projekt se liší od zmrazené výukové verze.")
    reference = hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()
    lexicon = read(LEXICON)
    timeline, all_cues, chapters, offset = [], [], [], 0.0
    # Čtení nezávislých hlaviček je na Windows omezené spouštěním procesů.
    # Paralelizujeme pouze read-only probe, nikoli mutace nebo samotný render.
    with ThreadPoolExecutor(max_workers=4) as workers:
        profiles = dict(
            zip(
                (scene["id"] for scene in plan),
                workers.map(
                    probe,
                    (ROOT / "video_course/recordings" / f"{scene['id']}.mp4" for scene in plan),
                ),
                strict=True,
            )
        )
    for scene in plan:
        clip = ROOT / "video_course/recordings" / f"{scene['id']}.mp4"
        receipt = read(clip.with_suffix(".json"))
        if receipt.get("status") != "recorded" or receipt.get("source_reference") != reference:
            raise ValueError(f"Chybí důkaz aktuálního skutečného záběru: {scene['id']}")
        audio = ROOT / receipt["audio"]
        speech = read(audio.with_suffix(".json"))
        spoken, changes = prepare(scene["paragraph"], lexicon)
        identity = hashlib.sha256(
            json.dumps(
                {
                    "audio": speech["signature"],
                    "screen": scene["screen"],
                    "source_reference": reference,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        if (
            speech["display_text"] != scene["paragraph"]
            or speech["spoken_text"] != spoken
            or sha256(audio) != speech["audio_sha256"]
            or identity != receipt["identity"]
        ):
            raise ValueError(f"Záběr neodpovídá aktuálnímu komentáři: {scene['id']}")
        duration, streams = profiles[scene["id"]]
        clip_hash = sha256(clip)
        if (
            receipt.get("clip_sha256") != clip_hash
            or receipt.get("clip_integrity_verification", {}).get("status") != "verified"
        ):
            raise ValueError(f"Chybí ověřený hash skutečného záběru: {scene['id']}")
        if abs(duration - receipt["duration"]) > 0.05:
            raise ValueError(f"Změnila se délka záběru: {scene['id']}")
        if not all(
            value in streams for value in ("1920x1080", "25 fps", "48000 Hz", "h264", "aac")
        ):
            raise ValueError(f"Nesouhlasí technický profil záběru: {scene['id']}")
        if scene["screen"]["kind"] == "terminal":
            expected = 1 if scene["screen"].get("action") == "failure" else 0
            if (receipt.get("terminal_result") or {}).get("exit_code") != expected:
                raise ValueError(f"Nedokončený nebo chybný skutečný příkaz: {scene['id']}")
            if scene["screen"].get("action") not in {"versions", "setup"}:
                proof = receipt.get("junit_result") or {}
                expected_failures = 1 if expected == 1 else 0
                if (
                    proof.get("testcases", 0) < 1
                    or proof.get("errors") != 0
                    or proof.get("failures") != expected_failures
                ):
                    raise ValueError(f"Chybí správný konkrétní JUnit: {scene['id']}")
                if sha256(ROOT / proof["junit"]) != proof["sha256"]:
                    raise ValueError(f"Změnil se konkrétní JUnit: {scene['id']}")
        cues = projected_words(scene["paragraph"], spoken, changes, speech["word_boundaries"])
        for cue in cues:
            if not 0 <= cue["start"] < cue["end"] <= duration + 0.05:
                raise ValueError(f"Titulky přesahují záběr: {scene['id']}")
            all_cues.append({**cue, "start": offset + cue["start"], "end": offset + cue["end"]})
        if not chapters or chapters[-1]["number"] != scene["chapter"]:
            chapters.append({"number": scene["chapter"], "title": scene["title"], "start": offset})
        timeline.append(
            {
                "scene": scene["id"],
                "chapter": scene["chapter"],
                "start": offset,
                "duration": duration,
                "clip": clip.relative_to(ROOT).as_posix(),
                "clip_sha256": clip_hash,
                "audio": audio.relative_to(ROOT).as_posix(),
                "audio_sha256": speech["audio_sha256"],
                "source_reference": reference,
                "terminal_result": receipt.get("terminal_result"),
            }
        )
        offset = round(offset + duration, 6)
    for index, chapter in enumerate(chapters):
        chapter["end"] = chapters[index + 1]["start"] if index + 1 < len(chapters) else offset
    if any(a["end"] > b["start"] + 0.001 for a, b in zip(all_cues, all_cues[1:], strict=False)):
        raise ValueError("Časy titulkových cues se překrývají.")
    return timeline, all_cues, chapters, offset


def ass_time(seconds):
    return timestamp(seconds)[:-1][1:]


def ass_text(text):
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", "\\N")


def metadata_text(text):
    for char in ("\\", "=", ";", "#"):
        text = text.replace(char, "\\" + char)
    return text.replace("\n", " ")


def prepare_files(directory, timeline, cues, chapters, duration, sample):
    directory.mkdir(parents=True, exist_ok=True)
    write_captions(cues, directory / "subtitles_cs")
    # Při concat jsou přesné skutečné délky včetně zaokrouhlení na snímky.
    lines = ["ffconcat version 1.0"]
    for clip in timeline:
        absolute = (ROOT / clip["clip"]).as_posix().replace("'", "'\\''")
        lines.extend([f"file '{absolute}'", f"duration {clip['duration']:.6f}"])
    (directory / "clips.ffconcat").write_text("\n".join(lines) + "\n", encoding="utf-8")
    metadata = [
        ";FFMETADATA1",
        f"title={metadata_text(TITLE)}",
        "comment=Skutečné záznamy; syntetický český komentář Microsoft Vlasta.",
    ]
    for chapter in chapters:
        metadata.extend(
            [
                "[CHAPTER]",
                "TIMEBASE=1/1000",
                f"START={round(chapter['start'] * 1000)}",
                f"END={round(chapter['end'] * 1000)}",
                f"title={metadata_text(str(chapter['number']) + '. ' + chapter['title'])}",
            ]
        )
    (directory / "chapters.ffmetadata").write_text("\n".join(metadata) + "\n", encoding="utf-8")
    (directory / "chapters.md").write_text(
        "# Kapitoly českého kurzu\n\n"
        + "\n".join(f"- {timestamp(c['start'])} — {c['number']}. {c['title']}" for c in chapters)
        + "\n",
        encoding="utf-8",
    )
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Label,Segoe UI,18,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,12,12,0,1
Style: Title,Segoe UI,32,&H00FFFFFF,&H00FFFFFF,&H80000000,&H80000000,-1,0,0,0,100,100,0,0,3,8,0,8,50,50,30,1
Style: Disclosure,Segoe UI,18,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,12,12,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for chapter in chapters:
        label = f"{chapter['number']:02} / 12  ·  {chapter['title']}"
        start, end = ass_time(chapter["start"]), ass_time(chapter["end"])
        events.append(f"Dialogue: 0,{start},{end},Label,,0,0,0,,{ass_text(label)}")
        intro_end = ass_time(min(chapter["end"], chapter["start"] + 3.5))
        events.append(
            f"Dialogue: 1,{start},{intro_end},Title,,0,0,0,," + r"{\fad(200,500)}" + ass_text(label)
        )
    events.append(
        "Dialogue: 0,0:00:00.00,0:00:08.00,Disclosure,,0,0,0,,"
        "Syntetický český komentář · Microsoft Vlasta"
    )
    (directory / "chapter_titles.ass").write_text(
        header + "\n".join(events) + "\n", encoding="utf-8"
    )
    manifest = {
        "sample_only": sample,
        "title": TITLE,
        "duration": duration,
        "scenes": timeline,
        "chapters": chapters,
        "caption_cues": len(cues),
        "voice": "cs-CZ-VlastaNeural",
        "audio_normalization": "loudnorm I=-16 TP=-1.5 LRA=11",
        "human_listening_review": "not_claimed",
    }
    (directory / "timeline.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    prior_validation = directory / "validation.json"
    if prior_validation.exists():
        prior = read(prior_validation)
        if any(
            not (ROOT / name).exists() or sha256(ROOT / name) != digest
            for name, digest in prior.get("linked_assets", {}).items()
        ):
            prior["status"] = "invalidated_by_changed_render_inputs"
            prior_validation.write_text(
                json.dumps(prior, ensure_ascii=False, indent=2), encoding="utf-8"
            )
    return manifest


def render(directory, duration, sample):
    filename = (
        "render_smoke_sample.mp4" if sample else "Playwright_Academy_Python_CZ_Full_Course.mp4"
    )
    target = directory / filename
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-y",
        "-hide_banner",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        "clips.ffconcat",
        "-i",
        "chapters.ffmetadata",
        "-i",
        "subtitles_cs.srt",
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-map",
        "2:0",
        "-map_metadata",
        "1",
        "-map_chapters",
        "1",
        "-vf",
        "ass=chapter_titles.ass",
        "-af",
        "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-threads",
        "4",
        "-crf",
        "21",
        "-pix_fmt",
        "yuv420p",
        "-r",
        "25",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        "-c:s",
        "mov_text",
        "-metadata:s:a:0",
        "language=ces",
        "-metadata:s:s:0",
        "language=ces",
        "-metadata:s:s:0",
        "title=Čeština",
        "-movflags",
        "+faststart",
        "-t",
        str(duration),
        target.name,
    ]
    with (directory / "render.log").open("w", encoding="utf-8") as log:
        subprocess.run(command, cwd=directory, stdout=log, stderr=log, check=True)
    validate(directory, duration, sample)


def validate(directory, duration, sample):
    filename = (
        "render_smoke_sample.mp4" if sample else "Playwright_Academy_Python_CZ_Full_Course.mp4"
    )
    target = directory / filename
    actual, streams = probe(target)
    if abs(actual - duration) > 0.2 or not all(
        x in streams for x in ("1920x1080", "25 fps", "aac", "mov_text")
    ):
        raise ValueError("Finální soubor nemá požadovanou délku nebo streamy.")
    if len(re.findall(r"Chapter #", streams)) != len(read(directory / "timeline.json")["chapters"]):
        raise ValueError("Finální MP4 nemá všechny kapitoly.")
    with (directory / "decode.log").open("w", encoding="utf-8") as log:
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-hide_banner",
                "-v",
                "error",
                "-i",
                str(target),
                "-map",
                "0:v:0",
                "-map",
                "0:a:0",
                "-f",
                "null",
                "-",
            ],
            stdout=log,
            stderr=log,
            check=True,
        )
    streams = streams.replace(str(ROOT), ".").replace(ROOT.as_posix(), ".")
    validation = {
        "status": "technically_validated",
        "file": target.relative_to(ROOT).as_posix(),
        "sha256": sha256(target),
        "bytes": target.stat().st_size,
        "duration": actual,
        "full_decode_exit_code": 0,
        "full_decode_error_log_bytes": (directory / "decode.log").stat().st_size,
        "probe": streams,
        "sample_only": sample,
        "human_listening_review": "not_claimed",
        "visual_review": "pending",
        "path_redaction": "Project root in FFmpeg probe replaced with relative dot; stream values unchanged",
        "linked_assets": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in [
                directory / name
                for name in (
                    "timeline.json",
                    "subtitles_cs.srt",
                    "subtitles_cs.vtt",
                    "chapters.md",
                    "chapter_titles.ass",
                )
            ]
            + [
                ROOT / "video_course/scripts/transcript_cs.md",
                ROOT / "video_course/reference_manifest.json",
            ]
        },
    }
    if validation["full_decode_error_log_bytes"]:
        raise ValueError("Úplné dekódování hlásí chybu; zkontrolujte decode.log.")
    (directory / "validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps({key: validation[key] for key in ("file", "duration", "bytes", "sha256")}),
        flush=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sample",
        nargs="+",
        help="Existující scény pro interní ověření renderu; nevydává se za kurz.",
    )
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument(
        "--validate-existing", action="store_true", help="Ověřit existující střih bez rekódování."
    )
    parser.add_argument(
        "--wait", action="store_true", help="Čekat na skutečné receipty všech 97 scén."
    )
    args = parser.parse_args()
    plan = read(ROOT / "video_course/storyboard/course_plan.json")
    if args.sample:
        plan = [s for s in plan if s["id"] in args.sample]
        if len(plan) != len(set(args.sample)):
            raise ValueError("Neexistující ukázková scéna.")
    elif len(plan) != 97 or sorted({s["chapter"] for s in plan}) != list(range(1, 13)):
        raise ValueError("Neúplný finální plán.")
    deadline = time.monotonic() + 3 * 3600
    while args.wait:
        missing = []
        for scene in plan:
            receipt = ROOT / "video_course/recordings" / f"{scene['id']}.json"
            if (
                not receipt.exists()
                or read(receipt).get("status") != "recorded"
                or not read(receipt).get("clip_integrity_verification", {}).get("status")
                == "verified"
            ):
                missing.append(scene["id"])
        if not missing:
            break
        print(json.dumps({"waiting_for_recordings": len(missing), "first": missing[0]}), flush=True)
        if time.monotonic() > deadline:
            raise TimeoutError("Čekání na skutečné záběry vypršelo.")
        time.sleep(30)
    directory = ROOT / (
        ("evidence/render-integration" if len(args.sample) > 1 else "evidence/render-smoke")
        if args.sample
        else "video_course/output"
    )
    # Během dlouhého natáčení mohou projít ještě schválené obsahové opravy.
    # Finální sběr vždy používá aktuální kanonický plán.
    latest = read(ROOT / "video_course/storyboard/course_plan.json")
    plan = [scene for scene in latest if not args.sample or scene["id"] in args.sample]
    timeline, cues, chapters, duration = collect(plan)
    prepare_files(directory, timeline, cues, chapters, duration, bool(args.sample))
    if args.validate_existing:
        validate(directory, duration, bool(args.sample))
    elif not args.prepare_only:
        render(directory, duration, bool(args.sample))


if __name__ == "__main__":
    main()
