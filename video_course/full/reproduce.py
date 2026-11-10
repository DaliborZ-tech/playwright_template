"""Rebuild both complete films from the delivered ZIP in a fresh path with spaces."""

import argparse
import hashlib
import json
import os
import site
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-extraction", type=Path)
    args = parser.parse_args()
    archive_path = ROOT / "dist/Playwright_Academy_Full_Course_Complete.zip"
    if args.reuse_extraction:
        extracted = args.reuse_extraction.resolve()
        assert extracted.is_relative_to((ROOT / ".tools/full-course-reproduction").resolve())
    else:
        extracted = (
            ROOT / ".tools/full-course-reproduction" / f"Delivered Course {int(time.time())}"
        )
        extracted.mkdir(parents=True, exist_ok=False)
        with zipfile.ZipFile(archive_path) as archive:
            assert archive.testzip() is None
            archive.extractall(extracted)
    manifest = json.loads((extracted / "MANIFEST_SHA256.json").read_text(encoding="utf-8"))
    assert all(sha(extracted / name) == digest for name, digest in manifest.items())
    sources = extracted / "production_sources"
    environment = os.environ.copy()
    media = ROOT / ".tools/media-env/Lib/site-packages"
    environment["PYTHONPATH"] = str(media) + os.pathsep + environment.get("PYTHONPATH", "")
    site.addsitedir(str(media))
    from imageio_ffmpeg import get_ffmpeg_exe

    environment["IMAGEIO_FFMPEG_EXE"] = get_ffmpeg_exe()
    evidence = HERE / "evidence/reproduction"
    evidence.mkdir(parents=True, exist_ok=True)
    with (evidence / "build.log").open("w", encoding="utf-8") as log:
        # PYTHONPATH alone does not process pywin32's .pth/DLL bootstrap.
        # Use the full existing production site exactly as the original build.
        bootstrap = (
            "import runpy,site,sys;from pathlib import Path;"
            "site.addsitedir(sys.argv[1]);script=Path(sys.argv[2]).resolve();"
            "sys.path.insert(0,str(script.parent));sys.argv=[str(script),'--assemble'];"
            "runpy.run_path(str(script),run_name='__main__')"
        )
        subprocess.run(
            [sys.executable, "-c", bootstrap, str(media), "video_course/full/build.py"],
            cwd=sources,
            env=environment,
            stdout=log,
            stderr=log,
            check=True,
        )
    rebuilt = sources / "video_course/full/output"
    names = (
        "Playwright_Academy_Python_CZ_Full_Course.mp4",
        "Playwright_Academy_Python_CZ_Full_Course_Titulky.mp4",
        "subtitles_cs.srt",
        "subtitles_cs.vtt",
        "chapters.json",
    )
    results = {}
    for name in names:
        original_sha, rebuilt_sha = sha(extracted / name), sha(rebuilt / name)
        assert original_sha == rebuilt_sha, name
        results[name] = original_sha
    report = {
        "result": "BYTE_IDENTICAL_FULL_COURSE_REBUILD_PASS",
        "files": results,
        "archive_tested_sha256": sha(archive_path),
        "render_inputs_sha256": sha(HERE / "render_inputs.json"),
        "extraction_relative_to_repository": str(extracted.relative_to(ROOT)),
        "environment": (
            "Fresh ZIP extraction and offline rebuild using the existing pinned Windows "
            "media environment and unchanged Windows fonts; not a clean OS installation"
        ),
        "tts_used": False,
        "new_capture_used": False,
    }
    (evidence / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
