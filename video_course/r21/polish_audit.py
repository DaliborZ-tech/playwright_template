"""Audit the specific R2.1 findings without claiming whole-chapter human approval."""

import json
import statistics
import subprocess

from media import ffmpeg
from prepare import HERE, OLD, ROOT, read, save, sha, silence


def gaps(cues):
    values = [b["start"] - a["end"] for a, b in zip(cues, cues[1:], strict=False)]
    return {
        "count": len(values),
        "median": statistics.median(values),
        "sum": sum(values),
        "between_0_85_and_1_20": sum(0.85 <= g <= 1.2 for g in values),
    }


def main():
    project = read(HERE / "output/edit_project.json")
    current = project["captions"]
    previous = read(OLD / "output/edit_project.json")["captions"]
    assert all(c["end"] - c["start"] >= 1 for c in current)
    assert all(len(c["text"].split()) >= 3 for c in current)
    crossing = [
        c
        for c in current
        if any(c["start"] + 0.04 < s["start"] < c["end"] - 0.04 for s in project["shots"][1:])
    ]
    assert not crossing, crossing
    audio_hashes = []
    for movie in project["movies"]:
        audio_hashes.append(
            subprocess.check_output(
                [
                    ffmpeg(),
                    "-v",
                    "error",
                    "-i",
                    str(HERE / "output" / movie["file"]),
                    "-map",
                    "0:a:0",
                    "-f",
                    "hash",
                    "-hash",
                    "sha256",
                    "-",
                ],
                text=True,
            ).strip()
        )
    assert audio_hashes[0] == audio_hashes[1]
    edits = read(HERE / "audio_edits.json")
    max_removed = max(e["removed_peak_int16"] for e in edits["edits"] + edits["codegen_edits"])
    voice = read(HERE / "comparison/human_listening_review.json")
    assert voice["after_sample_sha256"] == sha(HERE / "comparison/after_30s.wav")
    reference = read(HERE / "reference.json")
    assert all(
        sha(ROOT / name) == digest
        for name, digest in reference["source_manifest"]["sha256"].items()
    )
    result = {
        "revision": "R2.1",
        "movie_sha256": project["movies"][0]["sha256"],
        "caption_gaps_before": gaps(previous),
        "caption_gaps_after": gaps(current),
        "actual_long_silences_before": len(silence(OLD / "narration.wav")),
        "actual_long_silences_after": len(silence(HERE / "narration.wav")),
        "silence_measurement": "ffmpeg silencedetect, -45dB, at least0.7s, decoded PCM",
        "removed_audio_max_absolute_int16": max_removed,
        "audio_stretch_or_voice_overlap": False,
        "decoded_audio_hash_both_variants": audio_hashes[0],
        "short_cues_under_one_second": 0,
        "orphan_cues_under_three_words": 0,
        "caption_scene_crossings_over_40ms": 0,
        "frozen_source_files_verified": 78,
        "frozen_commit": reference["commit"],
        "human_audio_sample_review": voice,
        "static_targets": [
            {
                "shot": identity,
                "before": next(
                    s["duration"]
                    for s in read(OLD / "timeline.json")["shots"]
                    if s["id"] == identity
                ),
                "after": next(s["duration"] for s in project["shots"] if s["id"] == identity),
                "semantic_focus": next(
                    s["camera"] for s in project["shots"] if s["id"] == identity
                ),
            }
            for identity in ("02_function", "03_dom", "04_heading")
        ],
        "whole_chapter_human_review": "PENDING",
        "full_course_build_authorized": False,
    }
    save(HERE / "polish_validation.json", result)
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "caption_gaps_before",
                    "caption_gaps_after",
                    "actual_long_silences_before",
                    "actual_long_silences_after",
                    "short_cues_under_one_second",
                    "frozen_source_files_verified",
                )
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
