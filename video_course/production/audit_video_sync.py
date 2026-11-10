"""Porovná skutečnou zvukovou stopu sestřihu se zdrojovým hlasem každé scény."""

import argparse
import hashlib
import json
import re
import site
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
site.addsitedir(str(ROOT / ".tools/media-env/Lib/site-packages"))
import imageio_ffmpeg  # noqa: E402
import numpy as np  # noqa: E402

RATE = 16000


def pcm(path, start, duration):
    result = subprocess.run(
        [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-hide_banner",
            "-v",
            "error",
            "-ss",
            str(start),
            "-i",
            str(path),
            "-t",
            str(duration),
            "-vn",
            "-f",
            "f32le",
            "-ac",
            "1",
            "-ar",
            str(RATE),
            "pipe:1",
        ],
        capture_output=True,
        check=True,
    )
    return np.frombuffer(result.stdout, dtype=np.float32).astype(np.float64)


def alignment(reference, search):
    reference -= reference.mean()
    search -= search.mean()
    size = 1 << (len(reference) + len(search) - 1).bit_length()
    correlation = np.fft.irfft(
        np.fft.rfft(search, size) * np.conj(np.fft.rfft(reference, size)), size
    )
    energy = np.concatenate(([0.0], np.cumsum(search * search)))
    denominator = np.sqrt(
        np.dot(reference, reference) * (energy[len(reference) :] - energy[: -len(reference)])
    )
    scores = correlation[: len(denominator)] / np.maximum(denominator, 1e-12)
    best = int(np.argmax(scores))
    return best / RATE, float(scores[best])


def srt_cues(text):
    def seconds(value):
        hours, minutes, remainder = value.replace(",", ".").split(":")
        return int(hours) * 3600 + int(minutes) * 60 + float(remainder)

    cues = []
    for block in re.split(r"\n\s*\n", text.strip().replace("\r\n", "\n")):
        rows = block.splitlines()
        timing = next(i for i, row in enumerate(rows) if " --> " in row)
        start, end = rows[timing].split(" --> ")
        cues.append((seconds(start), seconds(end), " ".join(" ".join(rows[timing + 1 :]).split())))
    return cues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=ROOT / "video_course/output")
    args = parser.parse_args()
    directory = args.directory.resolve()
    validation = json.loads((directory / "validation.json").read_text(encoding="utf-8"))
    timeline = json.loads((directory / "timeline.json").read_text(encoding="utf-8"))
    video = ROOT / validation["file"]
    with video.open("rb") as stream:
        video_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    if video_hash != validation["sha256"]:
        raise ValueError("Video se liší od technicky validované verze.")

    def check_scene(scene):
        excerpt = min(4.0, scene["duration"] - 2)
        reference = pcm(ROOT / scene["audio"], 1.0, excerpt)
        search = pcm(video, scene["start"] + 0.5, excerpt + 1)
        position, correlation = alignment(reference, search)
        offset = (position - 0.5) * 1000
        return {
            "scene": scene["scene"],
            "expected_scene_start": scene["start"],
            "offset_ms": round(offset, 3),
            "normalized_correlation": round(correlation, 6),
            "status": "passed" if abs(offset) <= 80 and correlation >= 0.65 else "needs_review",
        }

    with ThreadPoolExecutor(max_workers=4) as workers:
        results = list(workers.map(check_scene, timeline["scenes"]))
    extracted = subprocess.run(
        [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-hide_banner",
            "-v",
            "error",
            "-i",
            str(video),
            "-map",
            "0:s:0",
            "-f",
            "srt",
            "pipe:1",
        ],
        capture_output=True,
        check=True,
    )
    embedded = srt_cues(extracted.stdout.decode("utf-8"))
    expected = srt_cues((directory / "subtitles_cs.srt").read_text(encoding="utf-8"))
    if len(embedded) != len(expected) or any(
        a[2] != b[2] for a, b in zip(embedded, expected, strict=True)
    ):
        raise ValueError("Vložená titulková stopa nezachovala přesný původní text.")
    timing_delta = max(
        max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a, b in zip(embedded, expected, strict=True)
    )
    if timing_delta > 0.002:
        raise ValueError("Vložená titulková stopa má jiný timing než dodané SRT.")
    report = {
        "video_sha256": video_hash,
        "embedded_subtitles": {
            "cues": len(embedded),
            "original_text_match": True,
            "max_timing_offset_ms": round(timing_delta * 1000, 3),
        },
        "status": "passed" if all(r["status"] == "passed" for r in results) else "needs_review",
        "method": (
            "Normalized waveform cross-correlation of source excerpts against rendered soundtrack"
        ),
        "scenes": len(results),
        "max_absolute_offset_ms": max(abs(r["offset_ms"]) for r in results),
        "human_listening_review": "not_claimed",
        "results": results,
    }
    (directory / "audio_alignment.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps({key: report[key] for key in ("status", "scenes", "max_absolute_offset_ms")}),
        flush=True,
    )
    if report["status"] != "passed":
        raise ValueError("Nesouhlasí skutečné časování audia; viz audio_alignment.json.")


if __name__ == "__main__":
    main()
