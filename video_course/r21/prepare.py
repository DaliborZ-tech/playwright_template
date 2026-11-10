"""R2.1: semantic silence edits, canonical balanced captions and auditable retiming."""

import hashlib
import importlib.util
import json
import math
import re
import site
import subprocess
import sys
import wave
from pathlib import Path

site.addsitedir(str(Path(__file__).resolve().parents[2] / ".tools/media-env/Lib/site-packages"))

import numpy as np  # noqa: E402
from media import ffmpeg, write_captions  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = ROOT / "video_course/r2"
sys.path.insert(0, str(ROOT / "video_course/production"))
spec = importlib.util.spec_from_file_location("r2_prepare", OLD / "prepare.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
RATE = 48000


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pcm(path):
    with wave.open(str(path)) as stream:
        assert stream.getframerate() == RATE and stream.getnchannels() == 1
        return np.frombuffer(stream.readframes(stream.getnframes()), dtype="<i2").copy()


def wav(path, samples):
    with wave.open(str(path), "wb") as stream:
        stream.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        stream.writeframes(samples.astype("<i2").tobytes())


def silence(path):
    result = subprocess.run(
        [
            ffmpeg(),
            "-hide_banner",
            "-i",
            str(path),
            "-af",
            "silencedetect=noise=-45dB:d=0.7",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", result.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", result.stderr)]
    return list(zip(starts, ends, strict=True))


def words(section, data):
    result = helper.word_map(
        section["paragraph"], data["spoken_text"], data["replacements"], data["word_boundaries"]
    )
    for i, word in enumerate(result):
        right = result[i + 1]["left"] if i + 1 < len(result) else len(section["paragraph"])
        word["text"] = section["paragraph"][word["left"] : right].strip()
    return result


def edits(intervals, shot_starts, section_starts, scale):
    result = []
    for start, end in intervals:
        if end - start < 0.7:
            continue
        if any(start <= t <= end + 0.20 for t in section_starts):
            target, reason = 0.68, "meaningful paragraph change"
        elif any(start <= t <= end + 0.20 for t in shot_starts):
            target, reason = 0.46, "on-screen task or view change"
        else:
            target, reason = 0.28, "connected explanation"
        keep = min(end - start, max(0.20, target * scale))
        count = max(0, round(((end - start) - keep) * RATE))
        left = round((start + keep / 2) * RATE)
        if count:
            result.append(
                {
                    "left": left,
                    "right": left + count,
                    "reason": reason,
                    "before": end - start,
                    "after": keep,
                }
            )
    return result


def apply(samples, cuts):
    parts, cursor = [], 0
    for cut in cuts:
        removed = samples[cut["left"] : cut["right"]]
        peak = int(np.abs(removed.astype(np.int32)).max(initial=0))
        assert peak < 190, ("Edit touches speech rather than measured quiet audio", peak)
        cut["removed_peak_int16"] = peak
        parts.append(samples[cursor : cut["left"]])
        cursor = cut["right"]
    parts.append(samples[cursor:])
    return np.concatenate(parts)


def mapped(at, cuts):
    sample = round(at * RATE)
    return (sample - sum(max(0, min(sample, c["right"]) - c["left"]) for c in cuts)) / RATE


def captions(text, word_list, boundaries):
    """Balanced canonical clauses, with penalties for orphan final words."""
    groups, start = [], 0
    for stop in range(1, len(word_list) + 1):
        is_sentence = bool(re.search(r"[.!?]$", word_list[stop - 1]["text"]))
        is_scene = stop == len(word_list) or any(
            word_list[stop - 1]["end"] <= t <= word_list[stop]["start"] for t in boundaries
        )
        if not (is_sentence or is_scene):
            continue
        group = word_list[start:stop]
        n = len(group)
        cost, back = [0] + [float("inf")] * n, [0] * (n + 1)
        for right in range(1, n + 1):
            for left in range(max(0, right - 22), right):
                content = " ".join(w["text"] for w in group[left:right])
                duration = group[right - 1]["end"] - group[left]["start"]
                if len(content) > 94 or duration > 7.5:
                    continue
                penalty = 1 + (len(content) - 62) ** 2 / 400
                penalty += 80 if right - left < 3 else 0
                penalty += 60 if duration < 1.35 else 0
                penalty += max(0, len(content) / max(duration, 0.1) - 23) * 3
                if cost[left] + penalty < cost[right]:
                    cost[right], back[right] = cost[left] + penalty, left
        if not math.isfinite(cost[n]):
            raise ValueError("No readable canonical caption split")
        chunks, cursor = [], n
        while cursor:
            left = back[cursor]
            chunks.append(
                {
                    "start": group[left]["start"],
                    "end": group[cursor - 1]["end"],
                    "text": " ".join(w["text"] for w in group[left:cursor]),
                }
            )
            cursor = left
        groups.extend(reversed(chunks))
        start = stop
    assert " ".join(c["text"] for c in groups) == " ".join(text.split())
    return groups


def main():
    old = read(OLD / "timeline.json")
    for name, digest in read(OLD / "capture_contract.json")["inputs_sha256"].items():
        assert sha(ROOT / name) == digest
    original = pcm(OLD / "narration.wav")
    cg_data = read(HERE / "codegen_narration.json")
    cg_audio = ROOT / cg_data["audio"]
    cg_wav = cg_audio.with_suffix(".wav")
    subprocess.run(
        [
            ffmpeg(),
            "-y",
            "-v",
            "error",
            "-i",
            str(cg_audio),
            "-ar",
            str(RATE),
            "-ac",
            "1",
            str(cg_wav),
        ],
        check=True,
    )
    cg_pcm = pcm(cg_wav)
    cg_cuts = edits(silence(cg_wav), [], [], 1.1)
    cg_pcm = apply(cg_pcm, cg_cuts)
    cg_duration = len(cg_pcm) / RATE
    intervals = silence(OLD / "narration.wav")
    low, high = 0.1, 3.0
    for _ in range(60):
        factor = (low + high) / 2
        cuts = edits(
            intervals,
            [s["voice_at"] for s in old["shots"]],
            [s["start"] for s in old["sections"]],
            factor,
        )
        length = len(original) - sum(c["right"] - c["left"] for c in cuts) + len(cg_pcm)
        if length < len(original):
            low = factor
        else:
            high = factor
    cuts = edits(
        intervals,
        [s["voice_at"] for s in old["shots"]],
        [s["start"] for s in old["sections"]],
        (low + high) / 2,
    )
    adjusted = apply(original, cuts)
    insertion_original = old["sections"][3]["start"]
    insertion = round(mapped(insertion_original, cuts) * RATE)
    output = np.concatenate((adjusted[:insertion], cg_pcm, adjusted[insertion:]))
    assert abs(len(output) - len(original)) < RATE / 100
    if len(output) < len(original):
        output = np.pad(output, (0, len(original) - len(output)))
    elif len(output) > len(original):
        assert not output[len(original) :].any()
        output = output[: len(original)]
    wav(HERE / "narration.wav", output)

    def project(at):
        return mapped(at, cuts) + (cg_duration if at >= insertion_original else 0)

    all_words, sections = [], []
    for section in old["sections"]:
        source = ROOT / section["audio"]
        local_words = words(section, read(source.with_suffix(".json")))
        offset = section["start"]
        for word in local_words:
            word.update(start=project(offset + word["start"]), end=project(offset + word["end"]))
        all_words.extend(local_words)
        sections.append({**section, "start": project(offset), "words": local_words})
    cg_section = {
        "id": "r21_codegen",
        "title": "Codegen vytvoří návrh, tester určí očekávání",
        "paragraph": cg_data["display_text"],
        "start": insertion / RATE,
        "voice": "cs-CZ-VlastaNeural",
        "audio": cg_data["audio"],
    }
    cg_words = words(cg_section, cg_data)
    for word in cg_words:
        word.update(
            start=insertion / RATE + mapped(word["start"], cg_cuts),
            end=insertion / RATE + mapped(word["end"], cg_cuts),
        )
    cg_section["words"] = cg_words
    sections.insert(3, cg_section)
    all_words.extend(cg_words)
    all_words.sort(key=lambda w: w["start"])
    shots = []
    for shot in old["shots"]:
        shifted_start = mapped(shot["start"], cuts)
        if shot["section"] >= "r2_04":
            shifted_start += cg_duration
        shots.append(
            {
                **shot,
                "start": round(shifted_start * 25) / 25,
                "voice_at": project(shot["voice_at"]),
                "parent_id": shot["id"],
            }
        )
    for action, cue in (
        ("cg_open", "Než lokátor"),
        ("cg_fill", "Do e-mailového"),
        ("cg_inspector", "V návrhu"),
    ):
        position = cg_section["paragraph"].index(cue)
        at = next(w["start"] for w in cg_words if w["left"] <= position < w["right"])
        shots.append(
            {
                "id": action,
                "on_screen_action": action,
                "view": "codegen",
                "start": round((insertion / RATE if action == "cg_open" else at) * 25) / 25,
                "voice_at": at,
                "voice_cue": cue,
                "section": "r21_codegen",
                "section_title": cg_section["title"],
                "expected_visible_state": action,
                "camera_focus": "Actual Codegen browser input and emitted Python in Inspector",
            }
        )
    shots.sort(key=lambda s: s["start"])
    for index, shot in enumerate(shots):
        end = (
            shots[index + 1]["start"]
            if index + 1 < len(shots)
            else math.ceil(len(output) / RATE * 25) / 25
        )
        shot.update(
            end=end,
            duration=round(end - shot["start"], 3),
            action_offset=max(0, shot["voice_at"] - shot["start"]),
        )
    transcript = " ".join(s["paragraph"] for s in sections)
    cues = captions(transcript, all_words, [s["start"] for s in shots[1:]])
    save(HERE / "captions.json", cues)
    write_captions(cues, HERE / "subtitles_cs")
    for section in sections:
        section.pop("shots", None)
    save(
        HERE / "timeline.json",
        {
            "revision": "R2.1",
            "voice": "cs-CZ-VlastaNeural",
            "title": old["title"],
            "duration": len(output) / RATE,
            "sections": sections,
            "shots": shots,
            "po_approval": "PENDING",
            "full_course_build_authorized": False,
        },
    )
    save(
        HERE / "audio_edits.json",
        {
            "parent_audio": str((OLD / "narration.wav").relative_to(ROOT)),
            "parent_sha256": sha(OLD / "narration.wav"),
            "edits": cuts,
            "codegen_edits": cg_cuts,
            "insert_at_parent_time": insertion_original,
            "insert_at_final_time": insertion / RATE,
            "insert_duration": cg_duration,
            "output_sha256": sha(HERE / "narration.wav"),
            "sample_rate": RATE,
            "phonemes_time_stretched": False,
            "human_listening_review": "PENDING",
        },
    )
    compare = HERE / "comparison"
    compare.mkdir(exist_ok=True)
    start = round(37.512 * RATE)
    after = round(project(37.512) * RATE)
    wav(compare / "before_30s.wav", original[start : start + 30 * RATE])
    wav(compare / "after_30s.wav", output[after : after + 30 * RATE])
    print(
        json.dumps(
            {
                "duration": len(output) / RATE,
                "shots": len(shots),
                "captions": len(cues),
                "short_cues": [c for c in cues if c["end"] - c["start"] < 1],
                "codegen_seconds": cg_duration,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
