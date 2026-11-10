"""Srovnávací český vzorek Jirka; stejné znění jako Microsoft Jakub."""

import json
import wave
from pathlib import Path

from piper import PiperVoice

ROOT = Path(__file__).resolve().parents[2]


def main():
    folder = ROOT / ".tools/piper-jirka"
    voice = PiperVoice.load(str(folder / "cs_CZ-jirka-medium.onnx"))
    text = (ROOT / "video_course/scripts/voice_sample.txt").read_text(encoding="utf-8")
    output = ROOT / "video_course/narration/voice_sample_jirka.wav"
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as file:
        voice.synthesize_wav(text, file)
    card = (folder / "MODEL_CARD").read_text(encoding="utf-8")
    licensing = ROOT / "video_course/production/JIRKA_MODEL_CARD.md"
    licensing.write_text(
        card + "\nSource: https://huggingface.co/rhasspy/piper-voices/"
        "tree/main/cs/cs_CZ/jirka/medium\n"
        "Engine: piper-tts 1.8.0, GPL-3.0; installed locally, model is not bundled.\n",
        encoding="utf-8",
    )
    with wave.open(str(output), "rb") as file:
        print(
            json.dumps(
                {
                    "voice": "Piper Jirka",
                    "seconds": file.getnframes() / file.getframerate(),
                    "sample_rate": file.getframerate(),
                    "path": str(output),
                }
            )
        )


if __name__ == "__main__":
    main()
