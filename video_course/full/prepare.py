"""Prepare the full course from verified Vlasta paragraphs using the accepted R2.1 cadence."""
# Authored Czech outcome sentences remain single serialized values.
# ruff: noqa: E501

import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "video_course/r21"))
spec = importlib.util.spec_from_file_location("r21_audio", ROOT / "video_course/r21/prepare.py")
audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audio)
import numpy as np  # noqa: E402
from media import ffmpeg  # noqa: E402

OUTCOMES = {
    1: "Převést předpoklad, krok a očekávaný výsledek manuálního případu do prvního regresního ověření.",
    2: "Ověřit Python, prostředí, závislosti a zvolený interpreter; skutečně spustit připravený projekt.",
    3: "Upravit krátkou Python funkci, vysvětlit proměnnou, argument, seznam, podmínku a návratovou hodnotu.",
    4: "Samostatně napsat první test a vysvětlit jeho skutečný RED→GREEN výsledek.",
    5: "Vybrat jednoznačný lokátor podle role, popisku, textu a test ID a ověřit jeho rozsah.",
    6: "Vyplnit skutečný formulář, zvolit hodnotu, uložit data a ověřit viditelný asynchronní výsledek.",
    7: "Spustit parametrizované případy, vysvětlit fixtures a ukázat nezávislost testů na pořadí.",
    8: "Projít vytvoření, úpravu, smazání a odhlášení ručně i skutečným regresním testem.",
    9: "Získat skutečný Codegen návrh, přečíst ho a doplnit vlastní srozumitelná očekávání.",
    10: "Vysvětlit skutečný assertion failure, najít jej v Trace Vieweru a ověřit opravu i Inspector.",
    11: "Spustit sadu, dohledat správný HTML/JUnit report a vysvětlit rozsah jeho výsledků.",
    12: "Ze zadání samostatně vytvořit a spustit test prázdného vyhledávání a určit další bezpečný krok.",
}


def main():
    approval = audio.read(ROOT / "video_course/r21/po_approval.json")
    assert approval["decision"] == "APPROVED" and approval["full_course_build_authorized"]
    for name, digest in approval["movies"].items():
        assert audio.sha(ROOT / "video_course/r21/output" / name) == digest
    reference = audio.read(ROOT / "video_course/r21/reference.json")
    assert all(
        audio.sha(ROOT / name) == digest
        for name, digest in reference["source_manifest"]["sha256"].items()
    )
    original = audio.read(ROOT / "video_course/storyboard/course_plan.json")
    cache = HERE / "audio_cache"
    cache.mkdir(parents=True, exist_ok=True)
    manifest = []
    for chapter in range(1, 13):
        selected = [s for s in original if s["chapter"] == chapter]
        folder = HERE / "chapters" / f"{chapter:02}"
        folder.mkdir(parents=True, exist_ok=True)
        if chapter == 4:
            entry = {
                "chapter": 4,
                "title": "První vlastní test",
                "learning_outcome": OUTCOMES[4],
                "status": "APPROVED_REFERENCE_REUSED",
                "duration": 348.48,
                "reference": "video_course/r21/output/edit_project.json",
            }
            audio.save(folder / "timeline.json", entry)
            manifest.append(entry)
            continue
        pieces, sections, all_words, offset = [], [], [], 0.0
        for source in selected:
            mp3 = ROOT / source["audio"]
            data = audio.read(mp3.with_suffix(".json"))
            assert data["voice"] == "cs-CZ-VlastaNeural" and audio.sha(mp3) == data["audio_sha256"]
            wav = cache / (source["id"] + "_" + data["audio_sha256"] + "_48k_mono_s16.wav")
            if not wav.exists():
                subprocess.run(
                    [
                        ffmpeg(),
                        "-y",
                        "-v",
                        "error",
                        "-i",
                        str(mp3),
                        "-ar",
                        "48000",
                        "-ac",
                        "1",
                        str(wav),
                    ],
                    check=True,
                )
            samples = audio.pcm(wav)
            intervals = audio.silence(wav)
            cuts = audio.edits(intervals, [], [], 1.1)
            samples = audio.apply(samples, cuts)
            # Paragraph boundaries retain a natural, sub-second transition.
            paragraph_end = math.ceil(len(samples) / 48000 * 25) / 25
            samples = np.pad(samples, (0, round(paragraph_end * 48000) - len(samples)))
            words = audio.words(source, data)
            for word in words:
                word.update(
                    start=offset + audio.mapped(word["start"], cuts),
                    end=offset + audio.mapped(word["end"], cuts),
                )
            section = {
                **source,
                "start": offset,
                "duration": paragraph_end,
                "words": words,
                "source_audio_sha256": audio.sha(mp3),
                "silence_edits": cuts,
            }
            section.pop("cues", None)
            section.pop("segments", None)
            sections.append(section)
            all_words.extend(words)
            pieces.append(samples)
            offset += paragraph_end
        audio.wav(folder / "narration.wav", np.concatenate(pieces))
        entry = {
            "chapter": chapter,
            "title": selected[0]["title"],
            "learning_outcome": OUTCOMES[chapter],
            "voice": "cs-CZ-VlastaNeural",
            "duration": round(offset, 3),
            "sections": sections,
            "frozen_commit": approval["frozen_commit"],
            "status": "AUDIO_PREPARED",
        }
        audio.save(folder / "timeline.json", entry)
        manifest.append({k: v for k, v in entry.items() if k != "sections"})
        print(
            json.dumps(
                {"chapter": chapter, "seconds": round(offset, 2), "paragraphs": len(sections)}
            ),
            flush=True,
        )
    audio.save(
        HERE / "course_manifest.json",
        {
            "revision": "FULL_R21_STANDARD",
            "chapters": manifest,
            "duration": sum(c["duration"] for c in manifest),
            "reference_po_approval": approval,
            "whole_course_product_acceptance": "PENDING",
        },
    )


if __name__ == "__main__":
    main()
