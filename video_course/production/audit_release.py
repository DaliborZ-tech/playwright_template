"""Nezávislé čtení hotové distribuce: CRC, manifesty, reference a přenositelnost."""

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT / "dist/Playwright_Academy"
PREFIX = "playwright-academy/"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--extract-to", type=Path)
    args = parser.parse_args()
    if args.extract_to and args.extract_to.exists():
        raise ValueError("Kontrolní rozbalení vyžaduje novou neexistující složku.")
    sums = (DELIVERY / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    for line in sums:
        expected, name = line.split("  ", 1)
        if Path(name).name != name or file_hash(DELIVERY / name) != expected:
            raise ValueError(f"Nesouhlasí distribuovaný soubor: {name}")
    merged, counts = {}, {}
    text_suffixes = {".py", ".ps1", ".json", ".md", ".toml", ".lock", ".cmd", ".html", ".xml"}
    for filename, manifest_name in (
        ("Playwright_Academy_Starter_Kit.zip", "RELEASE_MANIFEST.json"),
        ("Playwright_Academy_Production_Sources.zip", "PRODUCTION_MANIFEST.json"),
    ):
        with zipfile.ZipFile(DELIVERY / filename) as archive:
            if archive.testzip():
                raise ValueError(f"CRC chyba v {filename}")
            entries = json.loads(archive.read(PREFIX + manifest_name))
            names = {PREFIX + entry["path"] for entry in entries}
            if names | {PREFIX + manifest_name} != set(archive.namelist()):
                raise ValueError("Manifest nepokrývá přesně celý archiv.")
            for entry in entries:
                name = entry["path"]
                path = PurePosixPath(name)
                if path.is_absolute() or ".." in path.parts or "\\" in name:
                    raise ValueError("Nepřenositelná cesta v archivu.")
                if {".env", ".venv", ".tools", "__pycache__"} & set(path.parts):
                    raise ValueError("V distribuci je zakázaný soubor nebo prostředí.")
                data = archive.read(PREFIX + name)
                actual = digest(data)
                if actual != entry["sha256"]:
                    raise ValueError(f"Nesouhlasí manifest: {name}")
                if name in merged and merged[name] != actual:
                    raise ValueError(f"Archivy by se přepsaly rozdílnými daty: {name}")
                merged[name] = actual
                if path.suffix.lower() in text_suffixes:
                    text = data.decode("utf-8")
                    prefixes = re.findall(r"C:(?:\\+|/)Users(?:\\+|/)([^\\/\s\"<>]+)", text, re.I)
                    if any(value != "TRAINING" for value in prefixes):
                        raise ValueError(f"Osobní cesta v distribuovaném textu: {name}")
            counts[filename] = len(entries)
            if args.extract_to:
                archive.extractall(args.extract_to)
    with zipfile.ZipFile(DELIVERY / "Playwright_Academy_Starter_Kit.zip") as archive:
        frozen = json.loads(archive.read(PREFIX + "video_course/reference_manifest.json"))["sha256"]
        validation = json.loads(archive.read(PREFIX + "video_course/output/validation.json"))
    if any(merged.get(name) != expected for name, expected in frozen.items()):
        raise ValueError("Distribuce neodpovídá zmrazenému kódu.")
    for name, expected in validation["linked_assets"].items():
        if merged.get(name) != expected:
            raise ValueError(f"V archivu se změnil nebo chybí validovaný podklad: {name}")
    if file_hash(DELIVERY / Path(validation["file"]).name) != validation["sha256"]:
        raise ValueError("Distribuované MP4 neodpovídá úplné technické validaci.")
    for name in ("subtitles_cs.srt", "subtitles_cs.vtt", "chapters.md"):
        if file_hash(DELIVERY / name) != merged["video_course/output/" + name]:
            raise ValueError(f"Samostatný soubor se liší od archivovaného: {name}")
    if args.extract_to:
        directory = args.extract_to / "playwright-academy/video_course/output"
        playlist = (directory / "clips_portable.ffconcat").read_text(encoding="utf-8")
        for name in re.findall(r"^file '(.+)'$", playlist, flags=re.M):
            if not (directory / name).is_file():
                raise ValueError("Relativní playlist neodkazuje na přiložený klip.")
    report = {
        "status": "passed",
        "checksummed_delivery_files": len(sums),
        "archive_files": counts,
        "frozen_files_matched": len(frozen),
        "merged_without_conflicts": True,
        "personal_prefix_scan": "passed",
        "video_sha256": validation["sha256"],
        "portable_extraction": bool(args.extract_to),
    }
    (ROOT / "evidence/release-audit.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
