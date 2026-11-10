"""Nezávislé lokální rozpoznání skutečného zvuku; není to lidský poslech."""

import argparse
import hashlib
import json
import re
import site
import subprocess
import time
import unicodedata
from pathlib import Path

from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[2]
site.addsitedir(str(ROOT / ".tools/media-env/Lib/site-packages"))
import imageio_ffmpeg  # noqa: E402
import numpy as np  # noqa: E402


def tokens(text):
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.findall(r"\w+", text)


def distance(reference, hypothesis):
    previous = list(range(len(hypothesis) + 1))
    for i, left in enumerate(reference, 1):
        row = [i]
        for j, right in enumerate(hypothesis, 1):
            row.append(min(row[-1] + 1, previous[j] + 1, previous[j - 1] + (left != right)))
        previous = row
    return previous[-1]


def write_summary(results, total):
    summary = {
        "model": "Systran/faster-whisper-small",
        "completed": len(results),
        "selected": total,
        "audio_seconds": sum(r["duration"] for r in results),
        "languages": sorted({r["language"] for r in results}),
        "normalized_word_error_rate": sum(r["word_edits"] for r in results)
        / sum(r["reference_words"] for r in results),
        "flagged_scenes": [
            r["scene"]
            for r in results
            if r["language"] != "cs" or r["normalized_word_error_rate"] > 0.35
        ],
        "human_listening_review": "not_claimed",
    }
    (ROOT / "evidence/speech-asr-audit.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    plan = json.loads(
        (ROOT / "video_course/storyboard/course_plan.json").read_text(encoding="utf-8")
    )
    if args.limit:
        plan = plan[: args.limit]
    destination = ROOT / "evidence/asr"
    destination.mkdir(parents=True, exist_ok=True)
    snapshots = ROOT / ".tools/asr-models/models--Systran--faster-whisper-small/snapshots"
    local_models = [p for p in snapshots.glob("*") if (p / "model.bin").exists()]
    model = WhisperModel(
        str(local_models[0]) if local_models else "small",
        device="cpu",
        compute_type="int8",
        cpu_threads=2,
        num_workers=1,
        download_root=str(ROOT / ".tools/asr-models"),
    )
    results = []
    for scene in plan:
        audio = ROOT / scene["audio"]
        audio_sha256 = hashlib.sha256(audio.read_bytes()).hexdigest()
        target = destination / f"{scene['id']}.json"
        if target.exists():
            cached = json.loads(target.read_text(encoding="utf-8"))
            if cached.get("audio_sha256") == audio_sha256:
                results.append(cached)
                write_summary(results, len(plan))
                continue
        speech = json.loads(audio.with_suffix(".json").read_text(encoding="utf-8"))
        started = time.monotonic()
        decoded = subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-hide_banner",
                "-v",
                "error",
                "-i",
                str(audio),
                "-f",
                "f32le",
                "-ac",
                "1",
                "-ar",
                "16000",
                "pipe:1",
            ],
            capture_output=True,
            check=True,
        )
        pcm = np.frombuffer(decoded.stdout, dtype=np.float32)
        # Bez jazykové nápovědy a bez očekávaného přepisu v promptu.
        segments, info = model.transcribe(
            pcm, beam_size=3, vad_filter=False, condition_on_previous_text=False
        )
        segments = [
            {
                "start": s.start,
                "end": s.end,
                "text": s.text,
                "average_log_probability": s.avg_logprob,
            }
            for s in segments
        ]
        recognized = " ".join(s["text"].strip() for s in segments)
        reference = tokens(speech["spoken_text"])
        hypothesis = tokens(recognized)
        edits = distance(reference, hypothesis)
        result = {
            "scene": scene["id"],
            "chapter": scene["chapter"],
            "audio": audio.relative_to(ROOT).as_posix(),
            "audio_sha256": audio_sha256,
            "model": "Systran/faster-whisper-small",
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "processing_seconds": time.monotonic() - started,
            "reference_words": len(reference),
            "word_edits": edits,
            "normalized_word_error_rate": edits / max(1, len(reference)),
            "recognized_text": recognized,
            "segments": segments,
            "scope": (
                "Automatic recognition only; phonetic aliases and identifiers can cause mismatches"
            ),
            "human_listening_review": "not_claimed",
        }
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        results.append(result)
        print(
            json.dumps(
                {
                    key: result[key]
                    for key in (
                        "scene",
                        "language",
                        "normalized_word_error_rate",
                        "processing_seconds",
                    )
                }
            ),
            flush=True,
        )
        write_summary(results, len(plan))


if __name__ == "__main__":
    main()
