"""Ověří skutečné MP3, úplná metadata a původní text všech titulků."""

import hashlib
import json
import re
import site
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
site.addsitedir(str(ROOT / ".tools/media-env/Lib/site-packages"))
import imageio_ffmpeg  # noqa: E402
from continuous_speech import projected_words  # noqa: E402
from prepare_spoken_text import LEXICON, prepare  # noqa: E402


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def caption_text(path):
    blocks = path.read_text(encoding="utf-8").strip().split("\n\n")
    lines = []
    for block in blocks:
        if block.strip() == "WEBVTT":
            continue
        rows = block.splitlines()
        position = next(i for i, row in enumerate(rows) if " --> " in row)
        lines.extend(rows[position + 1 :])
    return normalize(" ".join(lines))


def main():
    plan = json.loads(
        (ROOT / "video_course/storyboard/course_plan.json").read_text(encoding="utf-8")
    )
    lexicon = json.loads(LEXICON.read_text(encoding="utf-8"))
    results = []
    for scene in plan:
        audio = ROOT / scene["audio"]
        speech = json.loads(audio.with_suffix(".json").read_text(encoding="utf-8"))
        digest = hashlib.sha256(audio.read_bytes()).hexdigest()
        spoken, replacements = prepare(scene["paragraph"], lexicon)
        if (
            digest != speech["audio_sha256"]
            or speech["display_text"] != scene["paragraph"]
            or spoken != speech["spoken_text"]
            or speech["voice"] != "cs-CZ-VlastaNeural"
        ):
            raise ValueError(f"Nesouhlasí aktuální komentář: {scene['id']}")
        cues = projected_words(scene["paragraph"], spoken, replacements, speech["word_boundaries"])
        if cues != speech["cues"]:
            raise ValueError(f"Neaktuální titulkové metadata: {scene['id']}")
        for suffix in (".srt", ".vtt"):
            if caption_text(audio.with_suffix(suffix)) != normalize(scene["paragraph"]):
                raise ValueError(f"Neúplné titulky {scene['id']}{suffix}")
        decoded = subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-hide_banner",
                "-i",
                str(audio),
                "-af",
                "volumedetect",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            text=True,
            errors="replace",
            check=True,
        )
        match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", decoded.stderr)
        hours, minutes, seconds = map(float, match.groups())
        duration = hours * 3600 + minutes * 60 + seconds
        volume = re.search(r"max_volume: ([^ ]+) dB", decoded.stderr).group(1)
        if volume == "-inf" or float(volume) < -35 or cues[-1]["end"] > duration + 0.1:
            raise ValueError(f"Tiché nebo neúplné audio: {scene['id']}")
        results.append(
            {
                "scene": scene["id"],
                "audio": audio.relative_to(ROOT).as_posix(),
                "sha256": digest,
                "duration": duration,
                "cues": len(cues),
                "max_volume_db": float(volume),
                "full_decode_exit_code": 0,
            }
        )
    report = {
        "status": "passed",
        "voice": "cs-CZ-VlastaNeural",
        "scenes": len(results),
        "caption_cues": sum(r["cues"] for r in results),
        "audio_seconds": sum(r["duration"] for r in results),
        "human_listening_review": "not_claimed",
        "files": results,
    }
    (ROOT / "evidence/speech-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {key: report[key] for key in ("status", "scenes", "caption_cues", "audio_seconds")}
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
