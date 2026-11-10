"""Malý skutečný pokus Edge TTS. Žádný Azure účet, žádné vypínání TLS ani obcházení chyb služby."""

import asyncio
import hashlib
import importlib.metadata
import json
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "video_course/voice_samples"


async def main():
    text_path = ROOT / "video_course/scripts/pronunciation_check.txt"
    text = text_path.read_text(encoding="utf-8")
    metadata = {
        "engine": "edge-tts",
        "version": importlib.metadata.version("edge-tts"),
        "text_source": str(text_path.relative_to(ROOT)),
        "characters_per_voice": len(text),
        "input_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "purpose": "short technical voice comparison only",
        "unlimited_service_claim_verified": False,
        "human_listening_review": "pending",
        "production_voice_changed": False,
        "results": [],
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    try:
        voices = await asyncio.wait_for(edge_tts.list_voices(), timeout=30)
        czech = [v for v in voices if v.get("Locale") == "cs-CZ"]
        metadata["available_czech_voices"] = [v.get("ShortName") for v in czech]
    except Exception as error:
        metadata["voice_list_error_type"] = type(error).__name__
        czech = []
    for name in ("cs-CZ-VlastaNeural", "cs-CZ-AntoninNeural"):
        target = OUTPUT / f"Edge_{name}_technical.mp3"
        if target.exists():
            metadata["results"].append(
                {"voice": name, "status": "already_exists", "file": str(target.relative_to(ROOT))}
            )
            continue
        try:
            # Přirozené tempo, výslovnost předáme bez fonetických náhrad pro férový poslech.
            speech = edge_tts.Communicate(
                text, name, rate="-3%", connect_timeout=15, receive_timeout=30
            )
            await asyncio.wait_for(speech.save(str(target)), timeout=55)
            if target.stat().st_size < 1000:
                raise ValueError("Audio output is too short")
            metadata["results"].append(
                {
                    "voice": name,
                    "status": "generated",
                    "file": str(target.relative_to(ROOT)),
                    "bytes": target.stat().st_size,
                    "audio_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                }
            )
        except Exception as error:
            metadata["results"].append(
                {"voice": name, "status": "failed", "error_type": type(error).__name__}
            )
        # Malý test, nikoliv hromadná generace nebo pokusy obejít omezení služby.
    path = ROOT / "evidence/edge-tts-probe.json"
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
