"""FFmpeg resolution for offline rendering without a desktop or TTS connection."""

import os
import site
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
site.addsitedir(str(ROOT / ".tools/media-env/Lib/site-packages"))


def ffmpeg():
    override = os.environ.get("IMAGEIO_FFMPEG_EXE")
    if override:
        return override
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def timestamp(seconds, comma=False):
    value = max(0, round(seconds * 1000))
    hours, value = divmod(value, 3_600_000)
    minutes, value = divmod(value, 60_000)
    secs, millis = divmod(value, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}{',' if comma else '.'}{millis:03}"


def write_captions(cues, target):
    srt, vtt = [], ["WEBVTT\n"]
    for number, cue in enumerate(cues, 1):
        words = cue["text"].split()
        if len(cue["text"]) <= 53 or len(words) < 2:
            lines = cue["text"]
        else:
            split = min(
                range(1, len(words)),
                key=lambda at: abs(len(" ".join(words[:at])) - len(" ".join(words[at:]))),
            )
            lines = " ".join(words[:split]) + "\n" + " ".join(words[split:])
        srt.append(
            f"{number}\n{timestamp(cue['start'], True)} --> "
            f"{timestamp(cue['end'], True)}\n{lines}\n"
        )
        vtt.append(f"{timestamp(cue['start'])} --> {timestamp(cue['end'])}\n{lines}\n")
    target.with_suffix(".srt").write_text("\n".join(srt), encoding="utf-8")
    target.with_suffix(".vtt").write_text("\n".join(vtt), encoding="utf-8")
