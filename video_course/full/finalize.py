"""Finish the current-source course, player validation and complete distribution."""

import argparse
import hashlib
import json
import os
import site
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(script, *arguments):
    print(json.dumps({"step": script, "args": list(arguments)}), flush=True)
    subprocess.run([sys.executable, str(HERE / script), *arguments], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    last = HERE / "chapters/12/output/edit_project.json"
    if args.wait:
        import psutil

        while True:
            workers = [
                p
                for p in psutil.process_iter(["name", "cmdline"])
                if p.info["name"] == "python.exe"
                and any(
                    "video_course" in a
                    and any(name in a for name in ("capture.py", "produce.py", "build.py"))
                    for a in (p.info["cmdline"] or [])
                )
            ]
            if last.exists() and not workers and not (HERE / "finalization.hold").exists():
                break
            time.sleep(3)
    if not last.exists():
        raise FileNotFoundError("All real chapter captures/renders must finish first")
    sources = {
        ROOT / name
        for name in (
            "video_course/full/build.py",
            "video_course/full/prepare.py",
            "video_course/r21/media.py",
            "video_course/r21/motion.py",
            "video_course/r21/prepare.py",
            "video_course/r2/prepare.py",
            "video_course/r21/captions.json",
            "video_course/r21/timeline.json",
            "video_course/r21/po_approval.json",
            "video_course/r21/output/Playwright_Academy_R21_Prvni_Test.mp4",
        )
    }
    for n in range(1, 13):
        if n == 4:
            continue
        stage = HERE / "chapters" / f"{n:02}"
        sources.update(
            stage / name
            for name in (
                "timeline.json",
                "narration.wav",
                "capture.json",
                "capture_contract.json",
                "beats.json",
            )
        )
        receipts = json.loads((stage / "capture.json").read_text(encoding="utf-8"))
        for receipt in receipts:
            sources.add(ROOT / receipt["clip"])
            if receipt.get("contract_path"):
                sources.add(ROOT / receipt["contract_path"])
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in sorted(sources)}
    fonts = []
    for name in ("segoeui.ttf", "segoeuib.ttf"):
        font = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / name
        fonts.append({"file": name, "sha256": sha(font), "redistributed": False})
    record = {
        "inputs_sha256": hashes,
        "windows_font_references": fonts,
        "scope": "Exact inputs frozen immediately before the final current-source build",
    }
    site.addsitedir(str(ROOT / ".tools/media-env/Lib/site-packages"))
    import imageio_ffmpeg
    import numpy
    import PIL

    media_exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
    record["runtime"] = {
        "python": sys.version.split()[0],
        "numpy": numpy.__version__,
        "Pillow": PIL.__version__,
        "imageio_ffmpeg": imageio_ffmpeg.__version__,
        "ffmpeg_sha256": sha(media_exe),
        "ffmpeg_version": subprocess.check_output(
            [str(media_exe), "-version"], text=True
        ).splitlines()[0],
    }
    save(HERE / "render_inputs.json", record)
    run("build.py", "--assemble")
    assert all(sha(ROOT / name) == digest for name, digest in hashes.items())
    from deliver import player

    player(HERE / "output")
    run("analyze.py", "--pixels")
    run("verify_player.py")
    run("deliver.py")
    run("reproduce.py")
    # The final ZIP adds the verified reproduction receipt; the movie inputs
    # and the already verified films remain exactly the same.
    assert all(sha(ROOT / name) == digest for name, digest in hashes.items())
    run("deliver.py")
    save(
        HERE / "finalization.json",
        {
            "status": "COMPLETE_DELIVERY_PENDING_OWNER_REVIEW",
            "render_inputs_sha256": sha(HERE / "render_inputs.json"),
            "human_full_course_acceptance": "PENDING",
        },
    )
    print("FULL COURSE, REAL PLAYER CHECKS AND COMPLETE ZIP FINISHED", flush=True)


if __name__ == "__main__":
    main()
