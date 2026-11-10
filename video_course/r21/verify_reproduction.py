"""Build and run the delivered sources from an independent directory with spaces."""

import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def render_inputs(directory):
    r2 = directory / "video_course/r21"
    reference = json.loads((r2 / "reference.json").read_text(encoding="utf-8"))
    contract = json.loads((r2 / "capture_contract.json").read_text(encoding="utf-8"))
    captures = json.loads((r2 / "capture.json").read_text(encoding="utf-8"))
    paths = set(reference["source_manifest"]["sha256"])
    paths.update(contract["inputs_sha256"])
    paths.update(r["clip"] for r in captures)
    paths.update(
        f"video_course/r21/{name}"
        for name in (
            "build.py",
            "media.py",
            "motion.py",
            "comparison/human_listening_review.json",
            "capture.json",
            "capture_contract.json",
        )
    )
    return {Path(name).as_posix(): sha(directory / name) for name in sorted(paths)}


def main():
    delivered = ROOT / "dist/Playwright_Academy_R21_Reference"
    target = ROOT / ".tools" / f"R21 independent reproduction {int(time.time())}"
    target.mkdir()
    # Start from the actual ZIP payload, not a checkout with hidden dependencies.
    import zipfile

    with zipfile.ZipFile(ROOT / "dist/Playwright_Academy_R21_Complete.zip") as stream:
        for entry in stream.infolist():
            if entry.filename.startswith("sources/"):
                # Archive names are validated against traversal before extraction.
                relative = Path(entry.filename).relative_to("sources")
                destination = (target / relative).resolve()
                if not destination.is_relative_to(target.resolve()):
                    raise ValueError("Source archive escapes the reproduction directory")
                if not entry.is_dir():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with stream.open(entry) as source, destination.open("wb") as output:
                        shutil.copyfileobj(source, output)
    reference = json.loads((HERE / "reference.json").read_text(encoding="utf-8"))
    for name, digest in reference["source_manifest"]["sha256"].items():
        assert sha(target / name) == digest, name
    bundle = target / "video_course/r21/starter-reference.bundle"
    clone = target / "bundle-check"
    subprocess.run(
        ["git", "clone", "--branch", "r2-frozen", str(bundle), str(clone)],
        check=True,
        capture_output=True,
    )
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=clone, text=True).strip()
    assert commit == reference["commit"]
    log = HERE / "reproduction_render.log"
    with log.open("w", encoding="utf-8") as stream:
        subprocess.run(
            [str(ROOT / ".tools/media-env/Scripts/python.exe"), "video_course/r21/build.py"],
            cwd=target,
            stdout=stream,
            stderr=stream,
            check=True,
        )
    project = json.loads((delivered / "edit_project.json").read_text(encoding="utf-8"))
    movies = []
    for movie in project["movies"]:
        actual = sha(target / "video_course/r21/output" / movie["file"])
        assert actual == movie["sha256"], movie["file"]
        movies.append({"file": movie["file"], "sha256": actual, "bit_exact": True})
    for name in ("subtitles_cs.srt", "subtitles_cs.vtt"):
        assert sha(target / "video_course/r21/output" / name) == sha(delivered / name)
    with (HERE / "reproduction_tests.log").open("w", encoding="utf-8") as stream:
        subprocess.run(
            [sys.executable, "-m", "pytest", "tests", "training/solutions", "-q"],
            cwd=target,
            stdout=stream,
            stderr=stream,
            check=True,
        )
    import xml.etree.ElementTree as ET

    tree = ET.parse(target / "reports/junit.xml")
    cases = tree.findall(".//testcase")
    assert cases and not tree.findall(".//failure") and not tree.findall(".//error")
    assert not tree.findall(".//skipped")
    result = {
        "status": "PASS",
        "source": "actual complete ZIP extracted to a fresh path with spaces",
        "frozen_files": len(reference["source_manifest"]["sha256"]),
        "commit": commit,
        "offline_render": "PASS",
        "movies": movies,
        "global_captions_bit_exact": True,
        "starter_and_solutions_cases": len(cases),
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "voice_service_used_for_offline_render": False,
        "render_environment": "existing pinned media venv, same Windows fonts/FFmpeg",
        "render_inputs_sha256": render_inputs(target),
        "human_watch_and_listen": "OWNER_REVIEW_REQUIRED",
        "po_approval": "PENDING",
    }
    (HERE / "reproduction_validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
