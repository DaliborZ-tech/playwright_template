"""Deliver the complete reference film, captions, player and independent source project."""

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def main():
    project = json.loads((HERE / "output/edit_project.json").read_text(encoding="utf-8"))
    player = HERE / "evidence/player/player_validation.json"
    check = json.loads(player.read_text(encoding="utf-8"))
    assert check["movie_sha256"] == project["movies"][0]["sha256"]
    assert check["subtitle_playback_test"] == "PASS"
    quality = json.loads((HERE / "quality_audit.json").read_text(encoding="utf-8"))
    assert quality["movie_sha256"] == project["movies"][0]["sha256"]
    target = ROOT / "dist/Playwright_Academy_R2_Reference"
    target.mkdir(parents=True, exist_ok=True)
    sources = target / "sources"
    source_r2 = sources / "video_course/r2"
    for movie in project["movies"]:
        assert sha(HERE / "output" / movie["file"]) == movie["sha256"]
        copy(HERE / "output" / movie["file"], target / movie["file"])
    for name in ("subtitles_cs.srt", "subtitles_cs.vtt", "edit_project.json"):
        copy(HERE / "output" / name, target / name)
    for name in ("player.html", "start_player.py", "transcript_cs.md"):
        copy(HERE / name, target / name)
    copy(HERE / "REPRODUCE_CZ.md", target / "README_CZ.md")
    copy(HERE / "STARTER_README.md", sources / "README.md")
    (target / "PREHRAT.cmd").write_text(
        '@echo off\ncd /d "%~dp0"\npy -3 start_player.py\npause\n', encoding="ascii"
    )
    reference = json.loads((HERE / "reference.json").read_text(encoding="utf-8"))
    for name, digest in reference["source_manifest"]["sha256"].items():
        assert sha(ROOT / name) == digest, name
        copy(ROOT / name, sources / name)
    # The source project includes the teaching manual and only production code;
    # legacy media and old acceptance declarations are not distribution inputs.
    for name in ("BEGINNER_WALKTHROUGH.md", "ARCHITECTURE.md", "KNOWN_LIMITATIONS.md"):
        copy(ROOT / "docs" / name, sources / "docs" / name)
    copy(
        ROOT / "video_course/reference_manifest.json",
        sources / "video_course/reference_manifest.json",
    )
    for name in (
        "studio.py",
        "open_studio.py",
        "record_course.py",
        "continuous_speech.py",
        "prepare_spoken_text.py",
        "prepare_workspace.py",
        "pronunciation_vlasta.json",
        "requirements-media.lock",
    ):
        copy(ROOT / "video_course/production" / name, sources / "video_course/production" / name)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in {".py", ".md", ".svg"}:
            copy(path, source_r2 / path.name)
    for name in (
        "plan.json",
        "timeline.json",
        "capture.json",
        "capture_contract.json",
        "reference.json",
        "pronunciation.json",
        "starter-reference.bundle",
        "narration.wav",
        "rehearsal.json",
    ):
        copy(HERE / name, source_r2 / name)
    timeline = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    for section in timeline["sections"]:
        audio = ROOT / section["audio"]
        for path in (
            audio,
            audio.with_suffix(".json"),
            audio.with_suffix(".srt"),
            audio.with_suffix(".vtt"),
        ):
            copy(path, sources / path.relative_to(ROOT))
    captures = json.loads((HERE / "capture.json").read_text(encoding="utf-8"))
    for receipt in captures:
        clip = ROOT / receipt["clip"]
        for path in (clip, clip.with_suffix(".json")):
            copy(path, sources / path.relative_to(ROOT))
    run_group = captures[0]["run_group"]
    evidence_folders = [
        HERE / "evidence" / run_group,
        HERE / "evidence/frames",
        HERE / "evidence/final_frames",
        HERE / "evidence/player",
    ]
    rehearsal = json.loads((HERE / "rehearsal.json").read_text(encoding="utf-8"))
    rehearsal_run = next(r["proof"]["junit"] for r in rehearsal if "junit" in r["proof"])
    evidence_folders.append((ROOT / rehearsal_run).parents[1])
    for folder in evidence_folders:
        for path in folder.rglob("*"):
            if path.is_file():
                copy(path, sources / path.relative_to(ROOT))
    for path in (HERE / "output").glob("*.json"):
        copy(path, source_r2 / "output" / path.name)
    for path in (HERE / "output").glob("*.ass"):
        copy(path, source_r2 / "output" / path.name)
    for path in (HERE / "rendered").glob("*.ass"):
        copy(path, source_r2 / "rendered" / path.name)
    for name in (
        "REVIEW_R2.md",
        "ACCEPTANCE_R2.md",
        "quality_audit.json",
        "FONT_REFERENCE.json",
        "reproduction_validation.json",
    ):
        if (HERE / name).exists():
            copy(HERE / name, target / name)
            copy(HERE / name, source_r2 / name)
    reproduction = HERE / "reproduction_validation.json"
    if reproduction.exists():
        tested = json.loads(reproduction.read_text(encoding="utf-8"))
        assert tested["status"] == "PASS"
        for name, digest in tested["render_inputs_sha256"].items():
            assert sha(sources / name) == digest, (
                f"Delivery differs from tested render input: {name}"
            )
    chapters = [
        {"start": s["start"], "title": s["section_title"]}
        for i, s in enumerate(project["shots"])
        if i == 0 or s["section"] != project["shots"][i - 1]["section"]
    ]
    (target / "chapters.json").write_text(
        json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    manifest = {
        "revision": "R2",
        "status": "READY_FOR_HUMAN_REVIEW",
        "po_approval": "PENDING",
        "full_course_build_authorized": False,
        "voice": "cs-CZ-VlastaNeural",
        "duration": project["duration"],
        "frozen_commit": reference["commit"],
        "sha256": {
            p.relative_to(target).as_posix(): sha(p)
            for p in sorted(target.rglob("*"))
            if p.is_file() and p.name != "MANIFEST.json"
        },
    }
    (target / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    archive = target.parent / "Playwright_Academy_R2_Complete.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3) as stream:
        for path in sorted(target.rglob("*")):
            if path.is_file():
                stream.write(path, path.relative_to(target).as_posix())
    with zipfile.ZipFile(archive) as stream:
        assert stream.testzip() is None
        for name, digest in manifest["sha256"].items():
            assert hashlib.sha256(stream.read(name)).hexdigest() == digest, name
    receipt = {
        "archive": str(archive.relative_to(ROOT)),
        "sha256": sha(archive),
        "bytes": archive.stat().st_size,
        "files": len(manifest["sha256"]) + 1,
        "zip_crc_and_payload_sha256": "PASS",
    }
    (HERE / "distribution_validation.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
