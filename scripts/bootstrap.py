"""Instalátor bez admin práv a bez změn systémové bezpečnosti (stdlib)."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if sys.version_info[:2] != (3, 12):
        print("Je vyžadován ověřený Python 3.12. Nainstalujte jej z python.org.")
        return 2
    python = ROOT / ".venv" / "Scripts" / "python.exe"
    if python.exists():
        result = subprocess.run(
            [str(python), "-c", "import sys; print(sys.version_info[:2])"],
            capture_output=True,
            text=True,
        )
        if result.returncode or result.stdout.strip() != "(3, 12)":
            print("Stávající .venv není Python 3.12. Přejmenujte ji a spusťte instalaci znovu.")
            return 2
    try:
        if not python.exists():
            print("Vytvářím oddělené prostředí .venv…", flush=True)
            subprocess.run([sys.executable, "-m", "venv", str(ROOT / ".venv")], check=True)
        env = {**os.environ, "PIP_DISABLE_PIP_VERSION_CHECK": "1"}
        for arguments in [
            ["-m", "pip", "install", "-r", "requirements.lock"],
            ["-m", "pip", "check"],
            ["-m", "playwright", "install", "chromium"],
        ]:
            subprocess.run([str(python), *arguments], cwd=ROOT, env=env, check=True)
        if not (ROOT / ".env").exists():
            shutil.copyfile(ROOT / ".env.example", ROOT / ".env")
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"\nInstalace nebyla dokončena: {error}")
        print("Síť: ověřte proxy, firemní CA a přístup k PyPI / Playwright CDN s IT.")
        print("Použijte schválené HTTPS_PROXY, PIP_CERT, NODE_EXTRA_CA_CERTS.")
        print("Nevypínejte ověřování certifikátů. Nápověda: training/troubleshooting/windows.md")
        return 1
    print("\nHOTOVO. Spusťte scripts\\run_smoke.cmd; demo pro testy startuje automaticky.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
