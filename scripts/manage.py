"""Jedno místo pro spouštěče; vždy vrací skutečný exit code procesu."""

import argparse
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "demo",
            "smoke",
            "regression",
            "visible",
            "single",
            "report",
            "trace",
            "codegen",
            "failure",
            "fix",
        ],
    )
    parser.add_argument("target", nargs="?")
    args = parser.parse_args()
    if args.action == "report":
        path = ROOT / "reports" / "report.html"
        if not path.is_file():
            print("Report ještě neexistuje. Nejprve spusťte smoke nebo regression.")
            return 2
        webbrowser.open(path.as_uri())
        return 0
    command = [sys.executable]
    if args.action == "demo":
        command += ["-m", "demo_app.app"]
    elif args.action == "trace":
        traces = list((ROOT / "reports").rglob("trace.zip"))
        path = (
            Path(args.target).resolve()
            if args.target
            else (max(traces, key=lambda p: p.stat().st_mtime) if traces else None)
        )
        if path is None or not path.is_file():
            print("Trace neexistuje. Nejprve spusťte run_failure.cmd nebo předejte cestu.")
            return 2
        command += ["-m", "playwright", "show-trace", str(path)]
    elif args.action == "codegen":
        command += [
            "-m",
            "playwright",
            "codegen",
            "--target=python-pytest",
            "--output=tests/examples/codegen_draft.py",
            "http://127.0.0.1:5000/login",
        ]
        print("Demo musí běžet přes start_demo.cmd. Draft není automaticky sbíraný test.")
    else:
        command += ["-m", "pytest"]
        command += {
            "smoke": ["-m", "smoke"],
            "regression": ["-m", "regression"],
            "visible": ["-m", "smoke", "--headed", "--slowmo=350"],
            "single": [args.target or "tests/examples/test_first_test.py::test_login_page"],
            "failure": [
                "tests/teaching",
                "--teaching-failure",
                "--html=reports/failure.html",
                "--junitxml=reports/failure.xml",
                "--output=reports/failure-artifacts",
            ],
            "fix": [
                "training/solutions/test_10_fixed.py",
                "--html=reports/fixed.html",
                "--junitxml=reports/fixed.xml",
                "--output=reports/fixed-artifacts",
            ],
        }[args.action]
    try:
        return subprocess.call(command, cwd=ROOT)
    except (OSError, KeyboardInterrupt) as error:
        print(f"Spuštění ukončeno: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
