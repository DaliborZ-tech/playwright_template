"""Exercise the exact frozen Starter Kit after fresh extraction to a path with spaces."""

import hashlib
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
README = (
    "# Playwright Academy — Python Starter Kit\n\n"
    "Začněte v docs/INSTALL_WINDOWS.md. Spusťte scripts/setup_windows.cmd, "
    "potom scripts/run_smoke.cmd. Úplná česká příručka je training/MANUAL.md, "
    "vlastní úkoly training/exercises/WORKBOOK.md.\n\n"
    "Použijte Python 3.12. Zdrojová reference: "
    "129d317771d91da04e31e8150a2111188f9ae51f (r2-frozen). "
    "Tento README doplňuje 78 přesně zmrazených souborů.\n"
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_starter(target):
    reference = json.loads((ROOT / "video_course/r21/reference.json").read_text(encoding="utf-8"))
    frozen = reference["source_manifest"]["sha256"]
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        data = {name: (ROOT / name).read_bytes() for name in frozen}
        assert all(
            hashlib.sha256(data[name]).hexdigest() == digest for name, digest in frozen.items()
        )
        data["README.md"] = README.encode("utf-8")
        for name, content in sorted(data.items()):
            item = zipfile.ZipInfo(name, date_time=(2026, 11, 10, 12, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            archive.writestr(item, content)
    return frozen


def main():
    evidence = HERE / "evidence/starter"
    evidence.mkdir(parents=True, exist_ok=True)
    target = ROOT / "dist/Playwright_Academy_Starter_Kit.zip"
    target.parent.mkdir(exist_ok=True)
    frozen = make_starter(target)
    extracted = (
        ROOT / ".tools/full-starter-verification" / f"Delivered Starter Kit {int(time.time())}"
    )
    extracted.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        archive.extractall(extracted)
    assert all(sha(extracted / name) == digest for name, digest in frozen.items())
    junit = evidence / "junit.xml"
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests",
        "training/solutions",
        "-q",
        f"--html={evidence / 'report.html'}",
        f"--junitxml={junit}",
        f"--output={evidence / 'artifacts'}",
        "--tracing=off",
        "--video=off",
    ]
    with (evidence / "test.log").open("w", encoding="utf-8") as log:
        completed = subprocess.run(command, cwd=extracted, stdout=log, stderr=log)
    tree = ET.parse(junit)
    cases = tree.findall(".//testcase")
    assert completed.returncode == 0 and len(cases) == 44
    assert not any(tree.findall(".//" + name) for name in ("failure", "error", "skipped"))
    assert all(sha(extracted / name) == digest for name, digest in frozen.items())
    report = {
        "decision": "PASS",
        "testcases": len(cases),
        "exit_code": completed.returncode,
        "archive": str(target.relative_to(ROOT)),
        "archive_sha256": sha(target),
        "extraction_relative_to_repository": str(extracted.relative_to(ROOT)),
        "frozen_files_checked": len(frozen),
        "environment": (
            "Existing pinned Python 3.12 environment; "
            "fresh extraction, not a clean Windows install"
        ),
        "junit_sha256": sha(junit),
        "cases": [case.attrib for case in cases],
    }
    (evidence / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
