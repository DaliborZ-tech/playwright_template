"""SHA-256 manifest výukové verze. Kontrola odmítne změněný kód."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "video_course/reference_manifest.json"
FOLDERS = ("demo_app", "tests", "test_data", "pages", "training", "tests_external", "scripts")


def current():
    files = [
        ROOT / name
        for name in (
            "pyproject.toml",
            "requirements.lock",
            "conftest.py",
            ".env.example",
            "docs/INSTALL_WINDOWS.md",
            "docs/azure-pipelines.yml",
        )
    ]
    for name in FOLDERS:
        files.extend(
            p
            for p in (ROOT / name).rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
        )
    return {
        str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        for path in sorted(files)
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    values = current()
    if args.check:
        expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["sha256"]
        changed = [
            key for key in expected.keys() | values.keys() if expected.get(key) != values.get(key)
        ]
        if changed:
            print("REFERENCE CHANGED: " + ", ".join(sorted(changed)))
            return 1
        print(f"Reference odpovídá: {len(values)} souborů.")
        return 0
    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(
        json.dumps({"version": "1.0.0", "sha256": values}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Zmrazeno {len(values)} souborů.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
