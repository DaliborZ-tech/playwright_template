"""Skutečná Vlasta s odděleným fonetickým vstupem; zachovává původní ukázku."""

import asyncio
import hashlib
import importlib.metadata
import json
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[2]


async def main():
    source = ROOT / "video_course/scripts/pronunciation_check_vlasta_spoken_v1.txt"
    output = ROOT / "video_course/voice_samples/Vlasta_technical_pronunciation_v1_raw.mp3"
    if output.exists():
        print("Existující audio zůstalo zachováno; pro nový pokus zvolte novou verzi.")
        return
    text = source.read_text(encoding="utf-8")
    speech = edge_tts.Communicate(
        text, "cs-CZ-VlastaNeural", rate="-3%", connect_timeout=15, receive_timeout=30
    )
    await asyncio.wait_for(speech.save(str(output)), timeout=55)
    if output.stat().st_size < 1000:
        raise ValueError("Služba nevytvořila dostatečně dlouhé audio.")
    metadata = {
        "voice": "cs-CZ-VlastaNeural",
        "edge_tts_version": importlib.metadata.version("edge-tts"),
        "spoken_input_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "audio_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "audio": str(output.relative_to(ROOT)),
        "bytes": output.stat().st_size,
        "pronunciation_method": "separate Czech phonetic speech input; no custom SSML",
        "human_listening_review": "pending",
        "pronunciation_accuracy_claimed": False,
    }
    (ROOT / "evidence/vlasta-pronunciation-v1.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(metadata, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
