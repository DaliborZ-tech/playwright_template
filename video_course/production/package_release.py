"""Distribuce z allowlistu; žádné venv, tajemství, historické hlasy ani osobní cesty."""

import argparse
import hashlib
import io
import json
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / "dist/Playwright_Academy"
SOURCE_FOLDERS = (
    "demo_app",
    "tests",
    "test_data",
    "pages",
    "training",
    "tests_external",
    "scripts",
    "docs",
    ".vscode",
)
SOURCE_FILES = (
    "README.md",
    "pyproject.toml",
    "requirements.lock",
    "conftest.py",
    ".gitignore",
    ".env.example",
)
PRODUCTION_JSON = (
    "pronunciation_vlasta.json",
    "voice_decision.json",
    "continuous_speech_jobs.json",
)
EXCLUDED_PARTS = {"__pycache__", ".venv", ".tools", ".pytest_cache", ".ruff_cache"}


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def files_in(folder):
    return sorted(
        path
        for path in folder.rglob("*")
        if path.is_file()
        and not (set(path.relative_to(folder).parts) & EXCLUDED_PARTS)
        and path.suffix not in {".pyc", ".part"}
        and path.name != ".env"
    )


def source_files():
    result = [ROOT / name for name in SOURCE_FILES]
    for name in SOURCE_FOLDERS:
        result.extend(files_in(ROOT / name))
    production = ROOT / "video_course/production"
    result.extend(
        path
        for path in production.iterdir()
        if path.suffix in {".py", ".ps1", ".lock"} or path.name in PRODUCTION_JSON
    )
    result.extend(
        [
            ROOT / "video_course/README.md",
            ROOT / "video_course/reference_manifest.json",
            ROOT / "video_course/storyboard/course_plan.json",
        ]
    )
    result.extend(
        ROOT / "video_course/scripts" / name
        for name in (
            "transcript_cs.md",
            "narration_additions.json",
            "narration_deepdives.json",
            "narration_walkthroughs.json",
            "narration_refinements.json",
            "presentation_refinements.json",
        )
    )
    result.extend(
        ROOT / "video_course/output" / name
        for name in (
            "subtitles_cs.srt",
            "subtitles_cs.vtt",
            "chapters.md",
            "timeline.json",
            "validation.json",
            "chapter_titles.ass",
            "audio_alignment.json",
        )
    )
    for name in (
        "frozen",
        "solutions",
        "recorded-commands",
        "recorded-artifacts",
        "screenshots",
        "video-contact-sheets",
        "release-final",
        "release-reverse",
        "asr",
        "final-video-frames",
    ):
        result.extend(files_in(ROOT / "evidence" / name))
    for name in (
        "installer-exit.json",
        "production-operations-preflight.json",
        "speech-validation.json",
        "speech-asr-audit.json",
        "recording-integrity.json",
        "interpreter-selection.json",
        "visual-review.json",
        "sanitized-trace-viewer-validation.json",
        "sanitized-trace-selected.png",
        "release-toolchain.json",
    ):
        path = ROOT / "evidence" / name
        if path.exists():
            result.append(path)
    result.append(ROOT / "evidence/codegen/original_codegen_draft.py")
    return sorted(set(result))


def scrub_text(text):
    # Opravují se pouze cesty/hostname v generovaných důkazech; testový kód,
    # očekávání, stdout výsledky a zmrazený manifest se nepřepisují.
    text = re.sub(r"C:(?:\\+|/)Users(?:\\+|/)[^\\/\s\"<>]+", "C:/Users/TRAINING", text, flags=re.I)
    return text


def payload(path):
    data = path.read_bytes()
    redactions = []
    relative = path.relative_to(ROOT).as_posix()
    if relative.startswith("evidence/") and path.suffix.lower() == ".zip":
        output = io.BytesIO()
        with (
            zipfile.ZipFile(io.BytesIO(data)) as original,
            zipfile.ZipFile(
                output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6
            ) as sanitized,
        ):
            for item in original.infolist():
                content = original.read(item.filename)
                try:
                    text = content.decode("utf-8")
                except UnicodeDecodeError:
                    text = None
                if text is not None:
                    scrubbed = scrub_text(text)
                    if scrubbed != text:
                        if item.filename.endswith((".trace", ".network")):
                            for line in scrubbed.splitlines():
                                if line.strip():
                                    json.loads(line)
                        content = scrubbed.encode("utf-8")
                        redactions.append(
                            f"Personal user-directory prefix replaced inside {item.filename}"
                        )
                sanitized.writestr(item, content)
        if redactions:
            data = output.getvalue()
    elif relative.startswith("evidence/") and path.suffix.lower() in {
        ".xml",
        ".json",
        ".html",
        ".md",
        ".txt",
    }:
        text = data.decode("utf-8")
        if path.suffix == ".xml":
            root = ET.fromstring(data)
            changed = False
            for suite in root.iter("testsuite"):
                changed = suite.attrib.pop("hostname", None) is not None or changed
            if changed:
                text = ET.tostring(root, encoding="unicode")
                redactions.append("JUnit hostname removed; test results unchanged")
        scrubbed = scrub_text(text)
        if scrubbed != text:
            redactions.append("Personal Windows user-directory prefix replaced")
        data = scrubbed.encode("utf-8")
    elif path.suffix.lower() in {".py", ".ps1", ".json", ".md", ".toml", ".lock", ".cmd", ".html"}:
        text = data.decode("utf-8")
        if scrub_text(text) != text:
            raise ValueError(f"Osobní cesta ve zdrojovém souboru: {relative}")
    return data, redactions


def make_zip(target, paths, manifest_name="RELEASE_MANIFEST.json"):
    manifest = []
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in paths:
            relative = path.relative_to(ROOT).as_posix()
            data, redactions = payload(path)
            archive.writestr("playwright-academy/" + relative, data)
            manifest.append(
                {
                    "path": relative,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "original_sha256": sha256(path),
                    "redactions": redactions,
                }
            )
        archive.writestr(
            "playwright-academy/" + manifest_name,
            json.dumps(manifest, ensure_ascii=False, indent=2).encode(),
        )
    with zipfile.ZipFile(target) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"Poškozený archiv: {bad}")
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    validation_path = ROOT / "video_course/output/validation.json"
    if not validation_path.exists():
        raise ValueError("Finální kurz ještě nemá technickou validaci.")
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if validation.get("status") != "technically_validated" or not validation.get("linked_assets"):
        raise ValueError(
            "Finální validace je neaktuální nebo neobsahuje vazbu na titulky a časovou osu."
        )
    for name, digest in validation["linked_assets"].items():
        if not (ROOT / name).exists() or sha256(ROOT / name) != digest:
            raise ValueError(f"Video není svázané s aktuálním produkčním podkladem: {name}")
    video = ROOT / validation["file"]
    timeline = json.loads((ROOT / "video_course/output/timeline.json").read_text(encoding="utf-8"))
    if (
        validation.get("sample_only")
        or len(timeline["scenes"]) != 97
        or len(timeline["chapters"]) != 12
    ):
        raise ValueError("Nelze distribuovat ukázku jako úplný kurz.")
    if sha256(video) != validation["sha256"] or validation.get("full_decode_exit_code") != 0:
        raise ValueError("Video neodpovídá úspěšné úplné technické validaci.")
    alignment = json.loads(
        (ROOT / "video_course/output/audio_alignment.json").read_text(encoding="utf-8")
    )
    if (
        alignment.get("status") != "passed"
        or alignment.get("scenes") != 97
        or alignment.get("video_sha256") != validation["sha256"]
    ):
        raise ValueError("Chybí ověření skutečné zvukové synchronizace finálního videa.")
    paths = source_files()
    if args.audit_only:
        for path in paths:
            payload(path)
        print(f"Allowlist ověřen: {len(paths)} souborů.")
        return
    DESTINATION.mkdir(parents=True, exist_ok=True)
    starter = DESTINATION / "Playwright_Academy_Starter_Kit.zip"
    source_manifest = make_zip(starter, paths)
    # Zmrazené soubory musí v distribuci zůstat byte-for-byte identické.
    frozen = json.loads(
        (ROOT / "video_course/reference_manifest.json").read_text(encoding="utf-8")
    )["sha256"]
    included = {entry["path"]: entry["sha256"] for entry in source_manifest}
    if any(included.get(name) != value for name, value in frozen.items()):
        raise ValueError("Distribuce změnila nebo vynechala zmrazený zdroj.")
    large_paths = []
    large_paths.extend(files_in(ROOT / "evidence/video-frames"))
    for scene in timeline["scenes"]:
        large_paths.extend([ROOT / scene["clip"], (ROOT / scene["clip"]).with_suffix(".json")])
        audio = ROOT / scene["audio"]
        large_paths.extend(
            audio.with_suffix(suffix) for suffix in (".mp3", ".json", ".srt", ".vtt")
        )
        if audio.with_suffix(".boundaries.json").exists():
            large_paths.append(audio.with_suffix(".boundaries.json"))
    large_paths.extend(
        ROOT / "video_course/output" / name
        for name in (
            "clips.ffconcat",
            "chapters.ffmetadata",
            "chapter_titles.ass",
            "timeline.json",
            "validation.json",
        )
    )
    # Concat playlist má při natáčení absolutní lokální cesty; pro přenos
    # používá relativní odkazy do stejného stromu zdrojového archivu.
    playlist = ROOT / "video_course/output/clips.ffconcat"
    portable = playlist.read_text(encoding="utf-8").replace(ROOT.as_posix() + "/", "../../")
    if scrub_text(portable) != portable:
        raise ValueError("Playlist nelze převést na přenositelnou podobu.")
    portable_path = ROOT / "video_course/output/clips_portable.ffconcat"
    portable_path.write_text(portable, encoding="utf-8")
    large_paths.remove(playlist)
    large_paths.append(portable_path)
    production = DESTINATION / "Playwright_Academy_Production_Sources.zip"
    make_zip(production, sorted(set(large_paths)), manifest_name="PRODUCTION_MANIFEST.json")
    for name in (video.name, "subtitles_cs.srt", "subtitles_cs.vtt", "chapters.md"):
        shutil.copy2(ROOT / "video_course/output" / name, DESTINATION / name)
    shutil.copy2(ROOT / "video_course/scripts/transcript_cs.md", DESTINATION / "transcript_cs.md")
    shutil.copy2(ROOT / "docs/PRODUCT_REPORT.md", DESTINATION / "DELIVERY.md")
    audit = ROOT / "evidence/release-audit.json"
    if audit.exists():
        shutil.copy2(audit, DESTINATION / "release-audit.json")
    products = sorted(
        path for path in DESTINATION.iterdir() if path.is_file() and path.name != "SHA256SUMS.txt"
    )
    (DESTINATION / "SHA256SUMS.txt").write_text(
        "\n".join(f"{sha256(path)}  {path.name}" for path in products) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "delivery": str(DESTINATION.relative_to(ROOT)),
                "files": len(products),
                "starter_files": len(source_manifest),
                "video_duration": validation["duration"],
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
