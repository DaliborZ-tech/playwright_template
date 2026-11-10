"""Extrahuje skutečné kapitoly a konec validovaného MP4 pro vizuální revizi."""

import hashlib
import json
import site
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
site.addsitedir(str(ROOT / ".tools/media-env/Lib/site-packages"))
import imageio_ffmpeg  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    directory = ROOT / "video_course/output"
    validation = json.loads((directory / "validation.json").read_text(encoding="utf-8"))
    timeline = json.loads((directory / "timeline.json").read_text(encoding="utf-8"))
    movie = ROOT / validation["file"]
    if validation.get("status") != "technically_validated" or sha256(movie) != validation["sha256"]:
        raise ValueError("Snímky vyžadují aktuální technicky validované video.")
    output = ROOT / "evidence/final-video-frames"
    output.mkdir(parents=True, exist_ok=True)
    points = [(f"chapter_{c['number']:02}", c["start"] + 1.5) for c in timeline["chapters"]]
    points.append(("ending", validation["duration"] - 1.5))
    plan = json.loads(
        (ROOT / "video_course/storyboard/course_plan.json").read_text(encoding="utf-8")
    )
    by_id = {scene["id"]: scene for scene in plan}
    chapter_starts = {chapter["start"] for chapter in timeline["chapters"]}
    for scene in timeline["scenes"]:
        kind = by_id[scene["scene"]]["screen"]["kind"]
        if scene["start"] not in chapter_starts and kind in {
            "browser",
            "codegen",
            "trace",
            "inspector",
        }:
            at = scene["start"] + (1.5 if kind == "browser" else 2.5)
            points.append((f"scene_{scene['scene']}_early", at))
    evidence = []
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 21)
    sheet = Image.new("RGB", (1920, ((len(points) + 2) // 3) * 395), "#111827")
    draw = ImageDraw.Draw(sheet)
    for index, (name, at) in enumerate(points):
        target = output / f"{name}.png"
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-y",
                "-hide_banner",
                "-v",
                "error",
                "-ss",
                str(at),
                "-i",
                str(movie),
                "-frames:v",
                "1",
                str(target),
            ],
            check=True,
        )
        x, y = (index % 3) * 640, (index // 3) * 395
        with Image.open(target) as frame:
            if frame.size != (1920, 1080):
                raise ValueError("Snímek nemá rozměry finálního videa.")
            sheet.paste(frame.resize((640, 360)), (x, y + 35))
        draw.text((x + 8, y + 3), f"{name} · {at:.2f} s", font=font, fill="white")
        evidence.append(
            {"file": target.relative_to(ROOT).as_posix(), "time": at, "sha256": sha256(target)}
        )
    sheet.save(output / "contact.jpg", quality=94)
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "video_sha256": validation["sha256"],
                "method": "Actual final MP4 frame extraction; chapter starts and ending",
                "visual_review": "pending",
                "frames": evidence,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Extrahováno {len(points)} skutečných finálních snímků.")


if __name__ == "__main__":
    main()
