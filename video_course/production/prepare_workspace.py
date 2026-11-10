"""Zapisovatelná kopie bez osobního jména v cestách, pouze pro skutečné natáčení."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = Path("C:/QA/PlaywrightAcademy")


def main():
    if TARGET.exists():
        raise SystemExit("Natáčecí složka již existuje. Nepřepisuji ji.")
    TARGET.mkdir(parents=True)
    for name in (
        "demo_app",
        "tests",
        "test_data",
        "pages",
        "training",
        "tests_external",
        "scripts",
    ):
        shutil.copytree(
            ROOT / name, TARGET / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
        )
    for name in ("README.md", "pyproject.toml", "requirements.lock", "conftest.py", ".env.example"):
        shutil.copyfile(ROOT / name, TARGET / name)
    shutil.copytree(ROOT / "docs", TARGET / "docs")
    evidence = {
        "recording_workspace": str(TARGET),
        "contains_real_credentials": False,
        "purpose": "Avoid personal username in IDE paths and real pytest output",
    }
    (ROOT / "evidence/recording-workspace.json").write_text(
        json.dumps(evidence, indent=2), encoding="utf-8"
    )
    print(TARGET)


if __name__ == "__main__":
    main()
