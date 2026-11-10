"""Independent file-level checks of narration continuity, captions and real action sources."""

import argparse
import hashlib
import json
import subprocess
import wave
import xml.etree.ElementTree as ET

from prepare import HERE, ROOT

# isort: split
import numpy as np
from media import ffmpeg


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def pcm(path):
    with wave.open(str(path)) as stream:
        assert stream.getframerate() == 48000
        assert stream.getnchannels() == 1 and stream.getsampwidth() == 2
        return stream.readframes(stream.getnframes())


def inspect_chapter(number, pixels=False):
    folder = HERE / "chapters" / f"{number:02}"
    project, plan = read(folder / "output/edit_project.json"), read(folder / "timeline.json")
    original, edited = pcm(folder / "narration.wav"), pcm(folder / "output/narration.wav")
    recovered, cursor, waits = [], 0, []
    sources, runs, prior_code = [], {}, None
    for shot in project["shots"]:
        original_count = shot["sample_end"] - shot["sample_start"]
        target_count = round(shot["duration"] * 48000)
        voiced = edited[cursor : cursor + original_count * 2]
        padding = edited[cursor + original_count * 2 : cursor + target_count * 2]
        assert voiced == original[shot["sample_start"] * 2 : shot["sample_end"] * 2]
        assert padding == b"\0" * len(padding)
        assert len(padding) == shot["audio_tail_padding_samples"] * 2
        recovered.append(voiced)
        cursor += target_count * 2
        waits.append(len(padding) / 96000)
        source = ROOT / shot["clip"]
        assert sha(source) == shot["clip_sha256"]
        proof = shot["proof"]
        identity = (
            proof.get("file"),
            proof.get("actual_selected_text"),
            proof.get("source_sha256"),
        )
        repeat = bool(proof.get("actual_selected_text") and identity == prior_code)
        prior_code = identity if proof.get("actual_selected_text") else None
        result = {
            "id": shot["id"],
            "action": shot["action"],
            "duration": shot["duration"],
            "source_sha256": shot["clip_sha256"],
            "same_code_state_as_previous": repeat,
            "declared_final_state_hold": shot["verified_final_state_hold_seconds"],
            "task_wait_seconds": len(padding) / 96000,
            "wait_edit": shot.get("wait_edit"),
        }
        if pixels:
            # Inspect original footage, before zoom/labels/subtitles. This is a
            # signal of pixel changes, never a claim of pedagogical approval.
            raw = subprocess.run(
                [
                    ffmpeg(),
                    "-v",
                    "error",
                    "-i",
                    str(source),
                    "-vf",
                    "fps=2,scale=160:90",
                    "-f",
                    "rawvideo",
                    "-pix_fmt",
                    "rgb24",
                    "-",
                ],
                capture_output=True,
                check=True,
            ).stdout
            frames = np.frombuffer(raw, np.uint8).reshape(-1, 90, 160, 3).astype(np.int16)
            deltas = (
                np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2, 3))
                if len(frames) > 1
                else np.zeros(1)
            )
            result.update(
                raw_sample_frames=len(frames),
                raw_max_rgb_delta=float(deltas.max()),
                raw_median_rgb_delta=float(np.median(deltas)),
                pixel_analysis_is_human_review=False,
            )
        sources.append(result)
        for candidate in (proof, proof.get("run", {})):
            if "junit" not in candidate:
                continue
            path = ROOT / candidate["junit"]
            assert sha(path) == candidate["junit_sha256"]
            tree = ET.parse(path)
            cases = tree.findall(".//testcase")
            assert len(cases) == candidate["testcases"]
            assert len(tree.findall(".//failure")) == candidate["failures"]
            assert not tree.findall(".//error") and not tree.findall(".//skipped")
            runs[str(path.relative_to(ROOT))] = {
                "cases": len(cases),
                "failures": candidate["failures"],
                "exit_code": candidate["exit_code"],
                "sha256": sha(path),
            }
    assert cursor == len(edited) and b"".join(recovered) == original
    cues = read(folder / "output/captions.json")
    assert " ".join(c["text"] for c in cues) == " ".join(
        " ".join(s["paragraph"] for s in plan["sections"]).split()
    )
    assert all(0 <= c["start"] < c["end"] <= project["duration"] for c in cues)
    assert all(a["end"] <= b["start"] + 0.001 for a, b in zip(cues, cues[1:], strict=False))
    report = {
        "chapter": number,
        "decision": "TECHNICAL_CHECKS_PASS",
        "original_pcm_recovered_byte_identically": True,
        "shots": sources,
        "duration": project["duration"],
        "canonical_captions": len(cues),
        "task_wait_total": sum(waits),
        "task_wait_maximum": max(waits),
        "actual_junit_runs": runs,
        "human_watch_and_listen": "PENDING_FULL_COURSE_REVIEW",
    }
    out = HERE / "evidence/analysis"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"chapter_{number:02}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "chapter": number,
                "duration": project["duration"],
                "pcm": "exact",
                "max_wait": max(waits),
                "cases": sum(r["cases"] for r in runs.values()),
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--chapters", type=int, nargs="+", default=[n for n in range(1, 13) if n != 4]
    )
    parser.add_argument("--pixels", action="store_true")
    args = parser.parse_args()
    for number in args.chapters:
        inspect_chapter(number, args.pixels)
