"""Průzkum skutečných nástrojů a hlasů. Nikdy nevyvozuje kvalitu z existence MP4."""

import json
import os
import platform
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    ps = (
        "Add-Type -AssemblyName System.Runtime.WindowsRuntime; "
        "$null=[Windows.Media.SpeechSynthesis.SpeechSynthesizer,"
        "Windows.Media.SpeechSynthesis,ContentType=WindowsRuntime]; "
        "@([Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | "
        "Select-Object DisplayName,Language) | ConvertTo-Json -Compress"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    voices = json.loads(result.stdout) if result.returncode == 0 and result.stdout.strip() else []
    if isinstance(voices, dict):
        voices = [voices]
    candidates = list((ROOT / ".tools/ffmpeg").glob("*/bin/ffmpeg.exe"))
    ffmpeg = shutil.which("ffmpeg") or (str(candidates[0]) if candidates else None)
    probe = shutil.which("ffprobe") or (
        str(candidates[0].with_name("ffprobe.exe")) if candidates else None
    )
    code = Path(os.environ["LOCALAPPDATA"]) / "Programs/Microsoft VS Code/Code.exe"
    data = {
        "platform": platform.platform(),
        "voices": voices,
        "jakub_available": any(
            v.get("DisplayName") == "Microsoft Jakub" and v.get("Language") == "cs-CZ"
            for v in voices
        ),
        "ffmpeg": ffmpeg,
        "ffprobe": probe,
        "vscode_installed": code.is_file(),
        "interactive_recording_verified": False,
        "human_listening_review": "not_performed",
    }
    output = ROOT / "evidence/video-preflight.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
