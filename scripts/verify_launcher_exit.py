"""Ověří skutečný návratový kód CMD pomocí izolovaného chybujícího bootstrapu."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parent = (ROOT / ".tools" / "launcher-check").resolve()
    assert parent.is_relative_to(ROOT.resolve())
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="with spaces ", dir=parent) as temp:
        folder = Path(temp).resolve()
        assert folder.is_relative_to(parent)
        (folder / "scripts").mkdir()
        (folder / ".venv" / "Scripts").mkdir(parents=True)
        shutil.copyfile(
            ROOT / "scripts" / "setup_windows.cmd", folder / "scripts/setup_windows.cmd"
        )
        shutil.copyfile(sys.executable, folder / ".venv/Scripts/python.exe")
        shutil.copyfile(ROOT / ".venv/pyvenv.cfg", folder / ".venv/pyvenv.cfg")
        (folder / "scripts/bootstrap.py").write_text("raise SystemExit(23)\n", encoding="utf-8")
        result = subprocess.run(
            ["cmd.exe", "/d", "/c", "scripts\\setup_windows.cmd"],
            cwd=folder,
            capture_output=True,
            text=True,
        )
        data = {
            "expected": 23,
            "actual": result.returncode,
            "pass": result.returncode == 23,
            "method": "actual CMD dispatcher, isolated Python bootstrap exits 23, path has spaces",
        }
        path = ROOT / "evidence" / "installer-exit.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(json.dumps(data))
        return 0 if data["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
