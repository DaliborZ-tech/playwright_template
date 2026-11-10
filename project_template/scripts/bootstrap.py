"""Vytvoření prostředí Python 3.12 bez aktivace PowerShell skriptů."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if sys.version_info[:2] != (3, 12):
        print("Použijte Python 3.12, například py -3.12 scripts\\bootstrap.py.")
        return 2
    python = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    try:
        if not python.exists():
            subprocess.run([sys.executable, "-m", "venv", str(ROOT / ".venv")], check=True)
        for arguments in (
            ["-m", "pip", "install", "-r", "requirements.lock"],
            ["-m", "pip", "check"],
            ["-m", "playwright", "install", "chromium"],
        ):
            subprocess.run([str(python), *arguments], cwd=ROOT, check=True)
        if not (ROOT / ".env").exists():
            shutil.copyfile(ROOT / ".env.example", ROOT / ".env")
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Instalace nebyla dokončena: {error}")
        return 1
    print("Hotovo. Nastavte BASE_URL v .env a spusťte scripts\\run_tests.cmd.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
