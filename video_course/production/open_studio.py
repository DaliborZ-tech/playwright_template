"""Otevře oddělený VS Code profil pro skutečný záznam bez osobních panelů."""

import argparse
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=ROOT)
    parser.add_argument("--enable-python", action="store_true")
    parser.add_argument("--r2", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    profile_name = (
        "studio-full-profile"
        if args.full
        else ("studio-r2-profile" if args.r2 else "studio-profile")
    )
    profile = ROOT / ".tools" / profile_name
    (profile / "User").mkdir(parents=True, exist_ok=True)
    settings = {
        "window.title": "Playwright Academy Studio Full"
        if args.full
        else ("Playwright Academy Studio R2" if args.r2 else "Playwright Academy Studio"),
        "window.restoreWindows": "none",
        "window.menuBarVisibility": "hidden",
        "workbench.startupEditor": "none",
        "workbench.colorTheme": "Default Dark Modern",
        "workbench.editor.enablePreview": False,
        "workbench.tips.enabled": False,
        "workbench.enableExperiments": False,
        "editor.fontSize": 21,
        "editor.lineHeight": 30,
        "editor.minimap.enabled": False,
        "editor.wordWrap": "on",
        "terminal.integrated.fontSize": 22,
        "terminal.integrated.tabs.enabled": False,
        "python.defaultInterpreterPath": str(args.workspace / ".venv/Scripts/python.exe"),
        "python.terminal.activateEnvironment": False,
        "python.REPL.sendToNativeREPL": False,
        "python.showStartPage": False,
        "terminal.integrated.defaultProfile.windows": "PowerShell",
        "workbench.panel.opensMaximized": "always",
        "terminal.integrated.env.windows": {"PYTHONUTF8": "1"},
        "breadcrumbs.enabled": False,
        "telemetry.telemetryLevel": "off",
        "security.workspace.trust.enabled": False,
        "update.mode": "none",
        "extensions.autoCheckUpdates": False,
        "extensions.autoUpdate": False,
        "extensions.ignoreRecommendations": True,
        "files.autoSave": "off",
        "git.enabled": False,
        "chat.disableAIFeatures": True,
        "workbench.secondarySideBar.defaultVisibility": "hidden",
    }
    if args.r2 or args.full:
        settings.update(
            {
                "editor.autoIndent": "none",
                "editor.autoClosingBrackets": "never",
                "editor.autoClosingQuotes": "never",
                "editor.formatOnType": False,
                "editor.quickSuggestions": False,
                "editor.wordBasedSuggestions": "off",
                "editor.suggestOnTriggerCharacters": False,
                "editor.acceptSuggestionOnEnter": "off",
                "files.eol": "\n",
                "editor.selectionBackground": "#27556b",
            }
        )
    (profile / "User" / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    code = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "Microsoft VS Code" / "Code.exe"
    if not code.exists():
        raise SystemExit("Není dostupný skutečný VS Code. Doplňte jeho schválenou instalaci.")
    environment = os.environ.copy()
    environment.pop("ELECTRON_RUN_AS_NODE", None)
    subprocess.Popen(
        [
            str(code),
            "--user-data-dir",
            str(profile),
            "--extensions-dir",
            str(ROOT / ".tools" / "studio-extensions"),
            "--new-window",
            "--disable-workspace-trust",
            *([] if args.enable_python else ["--disable-extensions"]),
            "--force-renderer-accessibility",
            "--skip-welcome",
            str(args.workspace),
            str(args.workspace / "README.md"),
        ],
        env=environment,
    )
    print("Otevírám oddělené skutečné okno Playwright Academy Studio.")


if __name__ == "__main__":
    main()
