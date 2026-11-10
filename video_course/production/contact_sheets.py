"""Přehledy skutečně extrahovaných snímků pro průběžnou vizuální kontrolu."""

import argparse
import json
import site
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
site.addsitedir(str(ROOT / ".tools/media-env/Lib/site-packages"))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", type=int)
    args = parser.parse_args()
    plan = json.loads(
        (ROOT / "video_course/storyboard/course_plan.json").read_text(encoding="utf-8")
    )
    reference = json.loads(
        (ROOT / "video_course/reference_manifest.json").read_text(encoding="utf-8")
    )["sha256"]
    import hashlib

    fingerprint = hashlib.sha256(json.dumps(reference, sort_keys=True).encode()).hexdigest()
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 21)
    target = ROOT / "evidence/video-contact-sheets"
    target.mkdir(parents=True, exist_ok=True)
    for number in [args.chapter] if args.chapter else range(1, 13):
        entries = [scene for scene in plan if scene["chapter"] == number]
        ready = []
        for scene in entries:
            receipt = ROOT / "video_course/recordings" / f"{scene['id']}.json"
            if not receipt.exists():
                continue
            evidence = json.loads(receipt.read_text(encoding="utf-8"))
            if (
                evidence.get("status") == "recorded"
                and evidence.get("source_reference") == fingerprint
            ):
                ready.append(scene)
        if len(ready) != len(entries):
            continue
        for fraction in range(3):
            sheet = Image.new("RGB", (1920, ((len(ready) + 2) // 3) * 395), "#111827")
            draw = ImageDraw.Draw(sheet)
            for index, scene in enumerate(ready):
                x, y = (index % 3) * 640, (index // 3) * 395
                frame = ROOT / "evidence/video-frames" / scene["id"] / f"{fraction}.png"
                with Image.open(frame) as image:
                    sheet.paste(image.resize((640, 360)), (x, y + 35))
                kind = scene["screen"]["kind"]
                label = f"{scene['id']} · {kind} · {('10%', '50%', '90%')[fraction]}"
                draw.text((x + 8, y + 3), label, font=font, fill="white")
            output = target / f"chapter_{number:02}_{fraction}.jpg"
            sheet.save(output, quality=94)
            print(str(output.relative_to(ROOT)), flush=True)


if __name__ == "__main__":
    main()
