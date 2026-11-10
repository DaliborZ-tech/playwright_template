"""Úplné dekódování a shoda tří archivovaných snímků před přijetím klipu."""

import argparse
import hashlib
import json
import site
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
site.addsitedir(str(ROOT / ".tools/media-env/Lib/site-packages"))
import imageio_ffmpeg  # noqa: E402
from PIL import Image  # noqa: E402


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def pixels(path):
    with Image.open(path) as image:
        return hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()


def verify(scene, reference):
    target = ROOT / "video_course/recordings" / f"{scene['id']}.mp4"
    receipt = target.with_suffix(".json")
    if not receipt.exists():
        return False
    try:
        initial_receipt = receipt.read_bytes()
        data = json.loads(initial_receipt)
    except json.JSONDecodeError:
        return False
    if data.get("status") != "recorded" or data.get("source_reference") != reference:
        return False
    before = sha256(target)
    prior = data.get("clip_sha256")
    if prior:
        if prior != before:
            raise ValueError(f"Přijatý klip byl později změněný: {scene['id']}")
        return True
    folder = ROOT / "evidence/recording-integrity" / scene["id"]
    folder.mkdir(parents=True, exist_ok=True)
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-hide_banner",
        "-v",
        "error",
        "-i",
        str(target),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-f",
        "null",
        "-",
    ]
    with (folder / "decode.log").open("w", encoding="utf-8") as log:
        subprocess.run(command, stdout=log, stderr=log, check=True)
    if (folder / "decode.log").stat().st_size:
        raise ValueError(f"Chyba úplného dekódování: {scene['id']}")
    matched = []
    for index, fraction in enumerate((0.1, 0.5, 0.9)):
        frame = folder / f"{index}.png"
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-y",
                "-hide_banner",
                "-v",
                "error",
                "-ss",
                str(data["duration"] * fraction),
                "-i",
                str(target),
                "-frames:v",
                "1",
                str(frame),
            ],
            check=True,
        )
        original = ROOT / "evidence/video-frames" / scene["id"] / f"{index}.png"
        if pixels(original) != pixels(frame):
            raise ValueError(f"Klip se liší od archivovaného snímku {scene['id']}/{index}.")
        matched.append(
            {
                "index": index,
                "fraction": fraction,
                "pixels_sha256": pixels(frame),
                "archived_png_sha256": sha256(original),
            }
        )
    if sha256(target) != before:
        raise ValueError(f"Klip se během verifikace změnil: {scene['id']}")
    if receipt.read_bytes() != initial_receipt:
        # Pozdější přetočení či zamítnutí se nesmí přepsat starou verifikací.
        return False
    data["clip_sha256"] = before
    data["clip_integrity_verification"] = {
        "status": "verified",
        "method": "full_decode_and_three_exact_archived_frame_matches",
        "full_decode_exit_code": 0,
        "matched_frames": matched,
        "scope": (
            "Technical integrity; visual source correctness and listening remain separate reviews"
        ),
    }
    temporary = receipt.with_suffix(".integrity.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(receipt)
    print(
        json.dumps({"scene": scene["id"], "status": "clip_integrity_verified", "sha256": before}),
        flush=True,
    )
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    plan = json.loads(
        (ROOT / "video_course/storyboard/course_plan.json").read_text(encoding="utf-8")
    )
    frozen = json.loads(
        (ROOT / "video_course/reference_manifest.json").read_text(encoding="utf-8")
    )["sha256"]
    reference = hashlib.sha256(json.dumps(frozen, sort_keys=True).encode()).hexdigest()
    deadline = time.monotonic() + 3 * 3600
    while True:
        verified = [scene["id"] for scene in plan if verify(scene, reference)]
        summary = {
            "verified": len(verified),
            "selected": len(plan),
            "scenes": verified,
            "source_reference": reference,
            "method": "Full decode plus three archived frame matches per clip",
        }
        (ROOT / "evidence/recording-integrity.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        if len(verified) == len(plan) or not args.watch:
            break
        if time.monotonic() > deadline:
            raise TimeoutError("Nedokončené skutečné záběry.")
        time.sleep(10)


if __name__ == "__main__":
    main()
