"""Run each chapter in its own process so repairs apply at chapter boundaries."""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    for number in [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12]:
        print(f"CAPTURE CHAPTER {number:02}", flush=True)
        result = subprocess.run(
            [sys.executable, str(HERE / "capture.py"), "--chapters", str(number), "--resume"],
            cwd=ROOT,
        )
        if result.returncode:
            raise SystemExit(result.returncode)
    print("ALL CHAPTER TAKES COMPLETED", flush=True)


if __name__ == "__main__":
    main()
