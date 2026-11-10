"""Evidence checks and raw-footage activity flags; never a pedagogical approval."""

import hashlib
import json
import site
import subprocess
import wave
import xml.etree.ElementTree as ET
from pathlib import Path

site.addsitedir(str(Path(__file__).resolve().parents[2] / ".tools/media-env/Lib/site-packages"))

import numpy as np  # noqa: E402
from media import ffmpeg  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    project = read(HERE / "output/edit_project.json")
    timeline = read(HERE / "timeline.json")
    receipts = read(HERE / "capture.json")
    assert project["voice"] == "cs-CZ-VlastaNeural"
    assert 300 <= project["duration"] <= 480
    # The final PCM is the original uninterrupted narration, plus only the final
    # <40ms video-frame padding. No silence may enter within a spoken paragraph.
    with wave.open(str(HERE / "narration.wav")) as stream:
        original_pcm = stream.readframes(stream.getnframes())
    with wave.open(str(HERE / "output/narration.wav")) as stream:
        final_pcm = stream.readframes(stream.getnframes())
    assert final_pcm.startswith(original_pcm)
    assert set(final_pcm[len(original_pcm) :]) <= {0}
    assert len(final_pcm) - len(original_pcm) < 3840
    # Canonical spelling survives the speech-only phonetic lexicon.
    transcript = " ".join(s["paragraph"] for s in timeline["sections"])
    captions = " ".join(c["text"] for c in project["captions"])
    assert transcript == captions
    previous_end = 0
    for cue in project["captions"]:
        assert previous_end <= cue["start"] < cue["end"] <= project["duration"]
        assert "\ufffd" not in cue["text"]
        previous_end = cue["end"]
    for name in ("subtitles_cs.srt", "subtitles_cs.vtt"):
        data = (HERE / "output" / name).read_bytes()
        assert data.decode("utf-8").encode("utf-8") == data
    by_action = {r["on_screen_action"]: r for r in receipts}
    red, green = [by_action[a]["proof"] for a in ("red_run", "green_run")]
    assert red["actual_junit_nodeid"] == green["actual_junit_nodeid"]
    assert red["exit_code"] == 1 and green["exit_code"] == 0
    for proof in (red, green):
        for path_key in ("junit", "browser_video", "report"):
            assert sha(ROOT / proof[path_key]) == proof[path_key + "_sha256"]
        tree = ET.parse(ROOT / proof["junit"])
        cases = tree.findall(".//testcase")
        assert len(cases) == 1 and not tree.findall(".//skipped")
        assert not tree.findall(".//error")
        assert len(tree.findall(".//failure")) == proof["failures"]
        actual_nodeid = (
            cases[0].attrib["classname"].replace(".", "/") + ".py::" + cases[0].attrib["name"]
        )
        assert actual_nodeid == proof["actual_junit_nodeid"]
    before = by_action["make_red"]["proof"]["text"]
    after = by_action["make_green"]["proof"]["text"]
    assert before.replace("Neexistující nadpis", "Přihlášení") == after
    assert after == (ROOT / "tests/examples/test_video_created.py").read_text(encoding="utf-8")
    flags, activity = [], []
    frames = HERE / "evidence/final_frames"
    frames.mkdir(exist_ok=True)
    for shot, receipt in zip(project["shots"], receipts, strict=True):
        assert shot["id"] == receipt["id"]
        clip = ROOT / receipt["clip"]
        # Raw frames only, before camera motion, labels and subtitles. Crop away
        # top window title and bottom taskbar. Small cursor/caret changes cannot
        # by themselves exceed the 0.4% changed-pixel threshold.
        pixels = subprocess.check_output(
            [
                ffmpeg(),
                "-v",
                "error",
                "-i",
                str(clip),
                "-vf",
                "crop=iw:ih-130:0:90,fps=2,scale=320:180,format=gray",
                "-f",
                "rawvideo",
                "-",
            ]
        )
        array = np.frombuffer(pixels, np.uint8).reshape((-1, 180, 320)).astype(np.int16)
        fraction = (np.abs(np.diff(array, axis=0)) > 12).mean(axis=(1, 2))
        quiet, longest = 0, 0
        for value in fraction:
            quiet = quiet + 0.5 if value < 0.004 else 0
            longest = max(longest, quiet)
        result = {
            "shot": shot["id"],
            "duration": shot["duration"],
            "longest_low_change_seconds": longest,
            "actual_action_interval": shot["actual_action_interval"],
            "capture_method": receipt["capture_method"],
        }
        activity.append(result)
        if longest >= 20:
            flags.append(
                {
                    **result,
                    "status": "REQUIRES_CONTENT_REVIEW",
                    "visible_subject": shot["expected_visible_state"],
                    "warning": (
                        "Camera, text overlays, mouse and metadata are not teaching activity."
                    ),
                }
            )
        at = min(shot["end"] - 0.25, shot["actual_action_interval"][1] + 1)
        png = frames / f"{shot['id']}.png"
        subprocess.run(
            [
                ffmpeg(),
                "-y",
                "-v",
                "error",
                "-ss",
                str(at),
                "-i",
                str(HERE / "output" / project["movies"][1]["file"]),
                "-frames:v",
                "1",
                str(png),
            ],
            check=True,
        )
    # Contact sheets are indexing aids, not a substitute for full-resolution review.
    for page in range(0, len(project["shots"]), 6):
        sheet = Image.new("RGB", (1280, 3 * 392), "#0c1421")
        draw = ImageDraw.Draw(sheet)
        for index, shot in enumerate(project["shots"][page : page + 6]):
            x, y = (index % 2) * 640, (index // 2) * 392
            shot_image = Image.open(frames / f"{shot['id']}.png").resize((640, 360))
            sheet.paste(shot_image, (x, y + 27))
            draw.text((x + 8, y + 6), f"{shot['id']}   {shot['start']:.2f}s", fill="white")
        sheet.save(frames / f"contact_{page // 6 + 1}.jpg", quality=92)
    result = {
        "status": "TECHNICAL_AND_EVIDENCE_CHECKS_COMPLETE",
        "movie_sha256": project["movies"][0]["sha256"],
        "duration": project["duration"],
        "shots": len(receipts),
        "voice": project["voice"],
        "uninterrupted_original_pcm": "PASS",
        "canonical_captions_utf8_timing": "PASS",
        "same_actual_junit_nodeid": red["actual_junit_nodeid"],
        "red_exit": 1,
        "green_exit": 0,
        "single_expected_value_change": "PASS",
        "final_code_matches_frozen_starter": "PASS",
        "activity": activity,
        "low_change_review_flags": flags,
        "visual_watch_and_listen": "OWNER_REVIEW_REQUIRED",
        "po_approval": "PENDING",
        "full_course_build_authorized": False,
    }
    (HERE / "quality_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"status": result["status"], "flags": flags}), flush=True)


if __name__ == "__main__":
    audit()
