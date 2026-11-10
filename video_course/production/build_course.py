"""Propojí české lekce, komentář, skutečné zdroje a měřitelné audio segmenty."""

import argparse
import json
import re
import shutil
import wave
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COURSE = ROOT / "video_course"

TITLES = [
    "Od manuálního testu k regresi",
    "Instalace a první spuštění",
    "Python pro testera",
    "První vlastní test",
    "Stabilní lokátory",
    "Akce a očekávání",
    "Projekt, fixtures a data",
    "Celá regresní cesta",
    "Codegen jako pomocník",
    "Selhání a diagnostika",
    "Regresní výsledky a reporty",
    "Váš samostatný test",
]
SOURCES = [
    "tests/smoke/test_login.py",
    "docs/INSTALL_WINDOWS.md",
    "training/solutions/test_03_python.py",
    "tests/examples/test_video_created.py",
    "training/solutions/test_05_locators.py",
    "tests/regression/test_records.py",
    "tests/conftest.py",
    "tests/regression/test_records.py",
    "training/solutions/test_09_codegen_refined.py",
    "tests/teaching/test_expected_failure.py",
    "docs/azure-pipelines.yml",
    "training/solutions/test_12_search.py",
]
ALIASES = {
    "Playwright": "plejrajt",
    "Pythonu": "pajtonu",
    "Pythonem": "pajtonem",
    "Python": "pajton",
    "pytestu": "pajtestu",
    "pytest": "pajtest",
    "Codegenu": "koud dženu",
    "Codegen": "koud džen",
    "Trace Viewer": "trejs vjúer",
    "BrowserContext": "brauzer kontext",
    "browser context": "brauzer kontext",
    "browser": "brauzer",
    "Browser": "brauzer",
    "fixtures": "fikščrs",
    "fixture": "fikščr",
    "Fixture": "fikščr",
    "assertions": "aséršns",
    "assertion": "aséršn",
    "Assertion": "aséršn",
    "Locator": "lokejtr",
    "locator": "lokejtr",
    "screenshot": "skrínšot",
    "Screenshot": "skrínšot",
    "slowmo": "slou mó",
    "slow": "slou",
    "dashboard": "dešbórd",
    "Dashboard": "dešbórd",
    "get_by_role": "get baj roul",
    "get_by_label": "get baj lejbl",
    "get_by_test_id": "get baj test aj dí",
    "to_be_visible": "tu bí vizibl",
    "to_have_count": "tu hev kaunt",
    "to_have_text": "tu hev tekst",
    "to_have_url": "tu hev jú ár el",
    "to_have_value": "tu hev veljú",
    "to_contain_text": "tu kontejn tekst",
    "Page Object": "pejdž obdžekt",
    "Page": "pejdž",
    "expect": "ikspekt",
    "goto": "gou tu",
    "fill": "fil",
    "click": "klik",
    "check": "ček",
    "select_option": "selekt opšn",
    "strict mode": "strikt mód",
    "auto-waiting": "auto wejting",
    "web-first": "web férst",
    "headless": "hedles",
    "headed": "hedyd",
    "traceback": "trejsbek",
    "trace": "trejs",
    "Trace": "trejs",
    "timeout": "tajmaut",
    "passed": "pást",
    "failed": "fejld",
    "skipped": "skipt",
    "deselected": "diselektid",
    "error": "eror",
    "return": "ritérn",
    "scope": "skoup",
    "session": "sešn",
    "context": "kontext",
    "label": "lejbl",
    "None": "nan",
    "Chromium": "kroumium",
    "Inspector": "inspektor",
    "Visual Studio Code": "vižual stúdio koud",
    "VS Code": "ví es koud",
    "HTML": "há té em el",
    "DOM": "dom",
    "CSS": "sí es es",
    "XPath": "eks pát",
    "API": "ej pí aj",
    "JUnit": "džej júnit",
    "XML": "eks em el",
    "CI": "sí aj",
    "URL": "jú ár el",
    "JSON": "džejson",
    "CSRF": "sí es ár ef",
}


def spoken_paragraph(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("**", "").replace("→", ", potom ")

    def inline(match):
        value = match.group(1)
        if "/" in value or "\\" in value or value.endswith((".py", ".cmd", ".html", ".xml", ".md")):
            return "odkazovaný soubor nebo příkaz"
        if "(" in value and len(value) > 35:
            return "zobrazený výraz"
        return value

    text = re.sub(r"`([^`]+)`", inline, text)
    text = text.replace("Ctrl+Shift+P", "Control Shift P").replace("Ctrl+C", "Control C")
    return re.sub(r"\s+", " ", text).strip()


def ssml(text: str) -> str:
    # Jediný hlas: žádné přepínání na anglického vypravěče uprostřed věty.
    pattern = re.compile("|".join(re.escape(k) for k in sorted(ALIASES, key=len, reverse=True)))
    parts, cursor = [], 0
    for match in pattern.finditer(text):
        if (match.start() and text[match.start() - 1].isalpha()) or (
            match.end() < len(text) and text[match.end()].isalpha()
        ):
            continue
        parts.append(escape(text[cursor : match.start()]))
        parts.append(
            f'<sub alias="{escape(ALIASES[match.group()], quote=True)}">'
            f"{escape(match.group())}</sub>"
        )
        cursor = match.end()
    parts.append(escape(text[cursor:]))
    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        'xml:lang="cs-CZ"><s>' + "".join(parts) + "</s></speak>"
    )


def screen(chapter: int, index: int, count: int) -> dict:
    base = {"kind": "editor", "source": SOURCES[chapter - 1], "line": 1}
    # Každá kapitola obsahuje skutečné akce, nikoli pouze textový výklad.
    changes = {
        1: {
            0: {"kind": "browser", "action": "overview"},
            2: {"kind": "terminal", "action": "regression"},
        },
        2: {
            0: {"kind": "terminal", "action": "versions"},
            2: {"kind": "terminal", "action": "setup"},
            4: {"kind": "browser", "action": "login"},
        },
        3: {2: {"kind": "terminal", "action": "python"}},
        4: {
            0: {"kind": "editor", "action": "write_first", "source": SOURCES[3]},
            4: {"kind": "terminal", "action": "first"},
        },
        5: {0: {"kind": "browser", "action": "login"}, 3: {"kind": "browser", "action": "search"}},
        6: {
            0: {"kind": "browser", "action": "create"},
            3: {"kind": "browser", "action": "api_error"},
        },
        7: {
            0: {"kind": "editor", "source": "tests/conftest.py", "line": 1},
            3: {"kind": "terminal", "action": "parametrize"},
            5: {"kind": "editor", "source": "pages/login_page.py", "line": 1},
        },
        8: {
            0: {"kind": "browser", "action": "journey"},
            3: {"kind": "terminal", "action": "journey"},
        },
        9: {
            0: {"kind": "codegen", "action": "record"},
            1: {"kind": "codegen", "action": "inspect"},
            2: {"kind": "editor", "source": "tests/examples/codegen_draft.py", "line": 1},
            4: {"kind": "terminal", "action": "refined"},
        },
        10: {
            0: {"kind": "terminal", "action": "failure"},
            2: {"kind": "trace", "action": "inspect"},
            3: {"kind": "editor", "source": "training/solutions/test_10_fixed.py", "line": 1},
            4: {"kind": "terminal", "action": "fixed"},
            5: {"kind": "inspector", "action": "debug"},
        },
        11: {
            0: {"kind": "terminal", "action": "regression"},
            1: {"kind": "browser", "action": "report"},
            2: {"kind": "editor", "source": "reports/junit.xml", "line": 1},
        },
        12: {
            0: {"kind": "editor", "source": "training/solutions/test_12_search.py", "line": 1},
            2: {"kind": "terminal", "action": "search"},
            3: {"kind": "browser", "action": "empty"},
            4: {"kind": "editor", "source": ".env.example", "line": 1},
        },
    }
    base.update(changes.get(chapter, {}).get(index, {}))
    if index == count - 1 and chapter not in {9, 10}:
        base = {"kind": "editor", "source": f"training/lessons/{chapter:02}.md", "line": 1}
    return base


def build(legacy_jakub=False):
    additions = json.loads(
        (COURSE / "scripts/narration_additions.json").read_text(encoding="utf-8")
    )
    deepdives = json.loads(
        (COURSE / "scripts/narration_deepdives.json").read_text(encoding="utf-8")
    )
    walkthrough_path = COURSE / "scripts/narration_walkthroughs.json"
    walkthroughs = (
        json.loads(walkthrough_path.read_text(encoding="utf-8"))
        if walkthrough_path.exists()
        else {}
    )
    current_plan = COURSE / "storyboard/course_plan.json"
    archive = COURSE / "storyboard/archive/course_plan_before_vlasta.json"
    if current_plan.exists() and not archive.exists():
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(current_plan, archive)
    refinement_path = COURSE / "scripts/narration_refinements.json"
    presentation_path = COURSE / "scripts/presentation_refinements.json"
    presentations = (
        json.loads(presentation_path.read_text(encoding="utf-8"))
        if presentation_path.exists()
        else {}
    )
    refinements = (
        json.loads(refinement_path.read_text(encoding="utf-8")) if refinement_path.exists() else {}
    )
    plan, jobs, transcript = [], [], []
    for chapter in range(1, 13):
        lesson = (ROOT / f"training/lessons/{chapter:02}.md").read_text(encoding="utf-8")
        lesson = re.sub(r"```.*?```", "", lesson, flags=re.S)
        lesson = re.sub(r"^#.*$", "", lesson, flags=re.M)
        paragraphs = [additions[f"{chapter:02}"]] + [
            spoken_paragraph(p) for p in re.split(r"\n\s*\n", lesson) if p.strip()
        ]
        paragraphs.append(deepdives[f"{chapter:02}"])
        if f"{chapter:02}" in walkthroughs:
            paragraphs.append(walkthroughs[f"{chapter:02}"])
        transcript.append(f"# {chapter:02} · {TITLES[chapter - 1]}\n")
        for index, paragraph in enumerate(paragraphs):
            scene_id = f"{chapter:02}_{index:02}"
            paragraph = refinements.get(scene_id, paragraph)
            folder = COURSE / "narration" / scene_id
            folder.mkdir(parents=True, exist_ok=True)
            sentences = (
                re.split(r"(?<=[.!?])\s+(?=[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ„])", paragraph)
                if legacy_jakub
                else [paragraph]
            )
            segments = []
            for number, sentence in enumerate(sentences):
                if legacy_jakub:
                    source, output = folder / f"{number:03}.ssml", folder / f"{number:03}.wav"
                    source.write_text(ssml(sentence), encoding="utf-8")
                    jobs.append(
                        {"text_path": str(source), "output_path": str(output), "ssml": True}
                    )
                    segments.append({"text": sentence, "wav": str(output.relative_to(ROOT))})
                else:
                    jobs.append(
                        {
                            "scene": scene_id,
                            "voice": "cs-CZ-VlastaNeural",
                            "display_text": sentence,
                            "unit": "continuous_paragraph",
                        }
                    )
            scene = {
                "id": scene_id,
                "chapter": chapter,
                "title": TITLES[chapter - 1],
                "paragraph": paragraph,
                "segments": segments,
                "screen": screen(chapter, index, len(paragraphs)),
                "narration_mode": "legacy_sentences" if legacy_jakub else "continuous_paragraph",
            }
            # Doplňující výklad zůstává nad skutečným kódem dané kapitoly.
            if index >= len(paragraphs) - 2:
                scene["screen"] = {"kind": "editor", "source": SOURCES[chapter - 1], "line": 1}
            scene["screen"] = presentations.get(scene_id, scene["screen"])
            plan.append(scene)
            transcript.append(f"## Scéna {scene_id}\n\n{paragraph}\n")
    (COURSE / "storyboard").mkdir(exist_ok=True)
    (COURSE / "storyboard/course_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    jobs_name = "speech_jobs.json" if legacy_jakub else "continuous_speech_jobs.json"
    (COURSE / "production" / jobs_name).write_text(
        json.dumps(jobs, ensure_ascii=False), encoding="utf-8"
    )
    (COURSE / "scripts/transcript_cs.md").write_text("\n".join(transcript), encoding="utf-8")
    (COURSE / "production/pronunciation.json").write_text(
        json.dumps(ALIASES, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "chapters": 12,
                "scenes": len(plan),
                "audio_segments": len(jobs),
                "words": sum(len(p["paragraph"].split()) for p in plan),
            },
            ensure_ascii=False,
        )
    )


def assemble_audio():
    path = COURSE / "storyboard/course_plan.json"
    plan = json.loads(path.read_text(encoding="utf-8"))
    total = 0.0
    for scene in plan:
        output = COURSE / "narration" / f"{scene['id']}.wav"
        position = 0.0
        with wave.open(str(output), "wb") as writer:
            for i, segment in enumerate(scene["segments"]):
                with wave.open(str(ROOT / segment["wav"]), "rb") as reader:
                    if i == 0:
                        writer.setparams(reader.getparams())
                    duration = reader.getnframes() / reader.getframerate()
                    segment["start"] = position
                    segment["end"] = position + duration
                    writer.writeframes(reader.readframes(reader.getnframes()))
                    # Krátký přirozený předěl; titulky mají přesný naměřený interval.
                    silence = round(reader.getframerate() * 0.12)
                    writer.writeframes(
                        b"\x00" * silence * reader.getsampwidth() * reader.getnchannels()
                    )
                    position += duration + silence / reader.getframerate()
        scene["audio"] = str(output.relative_to(ROOT))
        scene["duration"] = position
        total += position
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"audio_seconds": round(total, 2), "minutes": round(total / 60, 2)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--assemble-audio", action="store_true")
    parser.add_argument("--legacy-jakub", action="store_true")
    args = parser.parse_args()
    assemble_audio() if args.assemble_audio else build(args.legacy_jakub)
