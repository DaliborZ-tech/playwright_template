"""One complete R2.1 archive: movies, global captions, live proofs and editable sources."""

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from approval import apply as apply_approval

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / "video_course/r2"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def main():
    project_path = HERE / "output/edit_project.json"
    project = apply_approval(read(project_path), project_path.parent)
    project_path.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")
    assert read(HERE / "quality_audit.json")["movie_sha256"] == project["movies"][0]["sha256"]
    assert (
        read(HERE / "evidence/player/player_validation.json")["movie_sha256"]
        == project["movies"][0]["sha256"]
    )
    assert (
        read(HERE / "evidence/zoom/zoom_validation.json")["movie_sha256"]
        == project["movies"][0]["sha256"]
    )
    sample = read(HERE / "comparison/human_listening_review.json")
    assert sample["after_sample_sha256"] == sha(HERE / "comparison/after_30s.wav")
    target = ROOT / "dist/Playwright_Academy_R21_Reference"
    target.mkdir(parents=True, exist_ok=True)
    sources = target / "sources"
    for movie in project["movies"]:
        assert sha(HERE / "output" / movie["file"]) == movie["sha256"]
        copy(HERE / "output" / movie["file"], target / movie["file"])
    for name in ("subtitles_cs.srt", "subtitles_cs.vtt", "edit_project.json"):
        copy(HERE / "output" / name, target / name)
    for name in (
        "player.html",
        "start_player.py",
        "LIVE_EVIDENCE.md",
        "REVIEW_R21.md",
        "polish_validation.json",
        "quality_audit.json",
    ):
        copy(HERE / name, target / name)
    copy(HERE / "REPRODUCE_CZ.md", target / "README_CZ.md")
    if (HERE / "po_approval.json").exists():
        copy(HERE / "po_approval.json", target / "po_approval.json")
        copy(HERE / "APPROVAL_R21.md", target / "APPROVAL_R21.md")
    for path in (HERE / "comparison").iterdir():
        if path.is_file():
            copy(path, target / "comparison" / path.name)
    (target / "PREHRAT.cmd").write_text(
        '@echo off\ncd /d "%~dp0"\npy -3 start_player.py\npause\n', encoding="ascii"
    )
    reference = read(OLD / "reference.json")
    for name, digest in reference["source_manifest"]["sha256"].items():
        assert sha(ROOT / name) == digest
        copy(ROOT / name, sources / name)
    copy(HERE / "STARTER_README.md", sources / "README.md")
    for name in ("BEGINNER_WALKTHROUGH.md", "ARCHITECTURE.md", "KNOWN_LIMITATIONS.md"):
        copy(ROOT / "docs" / name, sources / "docs" / name)
    for name in (
        "studio.py",
        "open_studio.py",
        "record_course.py",
        "continuous_speech.py",
        "prepare_spoken_text.py",
        "requirements-media.lock",
        "pronunciation_vlasta.json",
    ):
        copy(ROOT / "video_course/production" / name, sources / "video_course/production" / name)
    copy(
        ROOT / "video_course/reference_manifest.json",
        sources / "video_course/reference_manifest.json",
    )
    # Preserve exact parent capture/audio inputs, not the former exported film.
    parent_inputs = {
        OLD / name
        for name in (
            "prepare.py",
            "capture.py",
            "media.py",
            "plan.json",
            "timeline.json",
            "capture.json",
            "capture_contract.json",
            "reference.json",
            "starter-reference.bundle",
            "narration.wav",
            "pronunciation.json",
            "output/edit_project.json",
            "REVIEW_R2.md",
        )
    }
    for name in read(OLD / "capture_contract.json")["inputs_sha256"]:
        parent_inputs.add(ROOT / name)
    for receipt in read(OLD / "capture.json"):
        parent_inputs.update(
            (ROOT / receipt["clip"], (ROOT / receipt["clip"]).with_suffix(".json"))
        )
    for path in parent_inputs:
        copy(path, sources / path.relative_to(ROOT))
    take = read(OLD / "capture.json")[0]["run_group"]
    for path in (OLD / "evidence" / take).rglob("*"):
        if path.is_file():
            copy(path, sources / path.relative_to(ROOT))
    for path in (OLD / "evidence/frames").glob("*.png"):
        copy(path, sources / path.relative_to(ROOT))
    for path in HERE.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".log", ".pyc"}:
            continue
        relative = path.relative_to(HERE)
        if relative.parts[0] == "rendered" and path.suffix != ".ass":
            continue
        if relative.parts[0] == "output" and path.name not in {
            "edit_project.json",
            "caption_overlay.ass",
        }:
            continue
        if path.name == "distribution_validation.json":
            continue
        copy(path, sources / path.relative_to(ROOT))
    chapters = [
        {"start": s["start"], "title": s["title"]} for s in read(HERE / "timeline.json")["sections"]
    ]
    (target / "chapters.json").write_text(
        json.dumps(chapters, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (target / "transcript_cs.md").write_text(
        "\n\n".join(
            f"## {s['title']}\n\n{s['paragraph']}" for s in read(HERE / "timeline.json")["sections"]
        ),
        encoding="utf-8",
    )
    reproduction = HERE / "reproduction_validation.json"
    if reproduction.exists():
        for name, digest in read(reproduction)["render_inputs_sha256"].items():
            assert sha(sources / name) == digest, name
        copy(reproduction, target / reproduction.name)
    manifest = {
        "revision": "R2.1",
        "status": project["status"],
        "full_course_build_authorized": project["full_course_build_authorized"],
        "whole_chapter_po_approval": project["po_approval"],
        "po_approval_evidence": project.get("po_approval_evidence"),
        "audio_sample_review": sample,
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
    archive = target.parent / "Playwright_Academy_R21_Complete.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=3) as stream:
        for path in sorted(target.rglob("*")):
            if path.is_file():
                stream.write(path, path.relative_to(target).as_posix())
    with zipfile.ZipFile(archive) as stream:
        assert stream.testzip() is None
        for name, digest in manifest["sha256"].items():
            assert hashlib.sha256(stream.read(name)).hexdigest() == digest
    result = {
        "archive": str(archive.relative_to(ROOT)),
        "sha256": sha(archive),
        "bytes": archive.stat().st_size,
        "files": len(manifest["sha256"]) + 1,
        "zip_crc_and_payload_sha256": "PASS",
    }
    (HERE / "distribution_validation.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
