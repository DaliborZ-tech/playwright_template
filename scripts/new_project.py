"""Založení samostatného projektu z explicitního seznamu souborů šablony."""

import argparse
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "project_template"
FILES = (
    ".env.example",
    ".gitignore",
    ".vscode/extensions.json",
    ".vscode/settings.json",
    "README.md",
    "conftest.py",
    "pages/__init__.py",
    "pages/README.md",
    "pyproject.toml",
    "requirements.lock",
    "scripts/bootstrap.py",
    "scripts/open_report.cmd",
    "scripts/run_tests.cmd",
    "scripts/setup_windows.cmd",
    "test_data/README.md",
    "tests/smoke/test_availability.py",
)


def project_name(value: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    name = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")
    if not name:
        raise ValueError("Název projektu musí obsahovat alespoň jedno písmeno nebo číslici.")
    return name


def payload(name: str) -> dict[str, bytes]:
    contents = {relative: (TEMPLATE / relative).read_bytes() for relative in FILES}
    for relative in ("README.md", "pyproject.toml"):
        contents[relative] = contents[relative].replace(b"playwright-tests", name.encode("ascii"))
    return contents


def create_project(destination: Path, name: str, init_git: bool = False) -> Path:
    target = destination.resolve()
    if target.is_relative_to(TEMPLATE.resolve()):
        raise ValueError("Cíl musí být mimo zdrojovou šablonu.")
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError("Cílová složka musí být nová nebo prázdná; nic se nepřepisuje.")
    if init_git and not shutil.which("git"):
        raise ValueError("Pro --git musí být dostupný příkaz git.")
    contents = payload(project_name(name))
    target.mkdir(parents=True, exist_ok=True)
    for relative, data in contents.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
    if init_git:
        subprocess.run(["git", "init", "-b", "main", str(target)], check=True)
    return target


def create_archive(destination: Path, name: str) -> Path:
    contents = payload(project_name(name))
    target = destination.resolve()
    if target.is_relative_to(TEMPLATE.resolve()):
        raise ValueError("Archiv ukládejte mimo zdrojovou šablonu.")
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "x", zipfile.ZIP_DEFLATED) as archive:
        for relative, data in contents.items():
            info = zipfile.ZipInfo(relative, date_time=(2026, 11, 10, 12, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, nargs="?", help="Nová nebo prázdná složka")
    parser.add_argument("--name", help="Název projektu; výchozí je název složky")
    parser.add_argument("--git", action="store_true", help="Založit samostatný Git na větvi main")
    parser.add_argument("--archive", type=Path, help="Místo projektu vytvořit samostatný ZIP")
    args = parser.parse_args()
    if bool(args.destination) == bool(args.archive):
        parser.error("Zadejte cílovou složku, nebo --archive; právě jednu z možností.")
    if args.archive and args.git:
        parser.error("--git patří k cílové složce, ne k archivu.")
    try:
        if args.archive:
            target = create_archive(args.archive, args.name or "playwright-tests")
        else:
            target = create_project(
                args.destination, args.name or args.destination.name, init_git=args.git
            )
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Projekt se nepodařilo vytvořit: {error}", file=sys.stderr)
        return 2
    print(f"Vytvořeno: {target}")
    if not args.archive:
        print("Pokračujte souborem README.md v novém projektu.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
