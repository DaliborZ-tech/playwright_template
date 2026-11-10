"""Measure real rendered geometric scaling, export visible zoom-in/return examples."""

import json
import site
import subprocess
from pathlib import Path

site.addsitedir(str(Path(__file__).resolve().parents[2] / ".tools/media-env/Lib/site-packages"))

import numpy as np  # noqa: E402
from media import ffmpeg  # noqa: E402
from PIL import Image  # noqa: E402

HERE = Path(__file__).resolve().parent


def longest_green_run(frame):
    # The outline is drawn in source coordinates BEFORE the entire screen zoom.
    # Its measured scale therefore follows code and source pixels, not a static crop.
    r, g, b = frame[:, :, 0], frame[:, :, 1], frame[:, :, 2]
    green = (g > 125) & (g > r * 1.4) & (b > r * 1.1) & (b < g * 0.9)
    green[:130] = False
    green[820:] = False
    best = 0
    # A five-row band tolerates subpixel interpolation/codec gaps in the stroke.
    for y in range(130, 816):
        points = np.flatnonzero(green[y : y + 5].any(axis=0))
        if len(points) > 350:
            span = int(points[-1] - points[0] + 1)
            if len(points) / span > 0.60:
                best = max(best, span)
    return best


def main():
    project = json.loads((HERE / "output/edit_project.json").read_text(encoding="utf-8"))
    output = HERE / "evidence/zoom"
    output.mkdir(exist_ok=True)
    results = []
    for identity in ("02_function", "04_heading"):
        shot = next(s for s in project["shots"] if s["id"] == identity)
        clip = HERE / "rendered" / (identity + ".mp4")
        begin, end = shot["camera"]["zoom_in_interval"]
        assert abs(end - begin - 2.4) < 0.001
        raw = subprocess.check_output(
            [
                ffmpeg(),
                "-v",
                "error",
                "-ss",
                str(begin),
                "-i",
                str(clip),
                "-t",
                "2.44",
                "-vf",
                "fps=10",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-",
            ]
        )
        frames = np.frombuffer(raw, np.uint8).reshape((-1, 1080, 1920, 3)).astype(np.float32)
        widths = [longest_green_run(frame) for frame in frames]
        positive = [w for w in widths if w > 400]
        assert len(positive) >= 20, widths
        assert positive[-1] / positive[0] > 1.28, widths
        # Smooth progression, not just two differently cropped still images.
        assert len(set(positive)) >= 15, widths
        assert min(np.diff(positive)) >= -12, widths
        for index in (0, len(frames) // 2, len(frames) - 1):
            Image.fromarray(frames[index].astype(np.uint8)).save(
                output / f"{identity}_{index:02}.png"
            )
        for name, interval in (("in", (begin, end)), ("return", shot["camera"]["return_interval"])):
            subprocess.run(
                [
                    ffmpeg(),
                    "-y",
                    "-v",
                    "error",
                    "-ss",
                    str(max(0, interval[0] - 0.2)),
                    "-i",
                    str(clip),
                    "-t",
                    str(interval[1] - interval[0] + 0.4),
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "18",
                    str(output / f"{identity}_{name}.mp4"),
                ],
                check=True,
            )
        results.append(
            {
                "shot": identity,
                "global_zoom_interval": [shot["start"] + begin, shot["start"] + end],
                "target": shot["camera"]["focus_subject"],
                "sample_fps": 10,
                "measured_source_outline_widths": widths,
                "measured_scale_ratio": positive[-1] / positive[0],
                "distinct_measured_sizes": len(set(positive)),
                "return_interval": shot["camera"]["return_interval"],
                "status": "PASS",
            }
        )
    (output / "zoom_validation.json").write_text(
        json.dumps(
            {"movie_sha256": project["movies"][0]["sha256"], "checks": results},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(results), flush=True)


if __name__ == "__main__":
    main()
