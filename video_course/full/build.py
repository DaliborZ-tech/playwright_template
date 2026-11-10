"""Offline, provenance-checked edit of genuine action takes and canonical narration.

No synthetic application frames are used. Final-state holds are explicit in the
timeline and are never counted as new activity. Longer tasks receive a measured
quiet waiting interval, preserving every original voiced PCM sample.
"""
# ASS styles are serialized records.
# ruff: noqa: E501

import argparse
import hashlib
import json
import math
import re
import subprocess
import time
import wave

from prepare import HERE, ROOT, audio

# prepare establishes the media environment and resolves the immutable R2.1 helpers.
# isort: split
from media import ffmpeg, timestamp, write_captions
from motion import expression


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def cache_hit(target, key_path, key):
    try:
        record = read(key_path)
        return record["input"] == key and target.exists() and record["output_sha256"] == sha(target)
    except (OSError, ValueError, TypeError, KeyError):
        return False


def cache_save(target, key_path, key):
    save(key_path, {"input": key, "output_sha256": sha(target)})


def source_focus(receipt, folder):
    """Find a single real selection row; reject whole-editor fallback boxes."""
    if not receipt["action"].startswith(("code:", "write:", "focus_code:")):
        return receipt["proof"].get("focus_rect"), None
    from PIL import Image

    frame = folder / "evidence" / receipt["take"] / "focus" / (receipt["id"] + ".png")
    frame.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "-v",
            "error",
            "-sseof",
            "-0.12",
            "-i",
            str(ROOT / receipt["clip"]),
            "-frames:v",
            "1",
            str(frame),
        ],
        frame.with_suffix(".log"),
    )
    import numpy as np

    pixels = np.asarray(Image.open(frame).convert("RGB")).astype(np.int16)
    mask = np.all(np.abs(pixels - [39, 85, 107]) < 10, axis=2)
    mask[:, :425] = False
    mask[:109] = False
    mask[1004:] = False
    rows = np.flatnonzero(mask.sum(axis=1) >= 30)
    groups = np.split(rows, np.where(np.diff(rows) > 1)[0] + 1)
    candidates = []
    for group in groups:
        if not 12 <= len(group) <= 40:
            continue
        ys, xs = np.nonzero(mask[group[0] : group[-1] + 1])
        if len(xs):
            candidates.append(
                (
                    len(xs),
                    [int(xs.min()), int(group[0]), int(xs.max() - xs.min() + 1), int(len(group))],
                )
            )
    rect = max(candidates, key=lambda item: item[0])[1] if candidates else None
    return rect, {
        "method": "single_row_component_of_actual_native_selection_pixels",
        "rect": rect,
        "verified_single_line": rect is not None,
        "source_frame": str(frame.relative_to(ROOT)),
        "source_frame_sha256": sha(frame),
        "fallback_outline_enabled": False,
    }


def run(command, target, cwd=None):
    with target.open("w", encoding="utf-8") as log:
        subprocess.run(
            [ffmpeg(), "-y", "-hide_banner", *command], cwd=cwd, stdout=log, stderr=log, check=True
        )


def esc(text):
    return text.replace("\\", "\\\\").replace("{", r"\{").replace("}", r"\}").replace("\n", r"\N")


def ass_time(at):
    return timestamp(at)[1:-1]


def approved_reference_captions(movie):
    import html

    result = subprocess.run(
        [ffmpeg(), "-v", "error", "-i", str(movie), "-map", "0:s:0", "-f", "srt", "-"],
        capture_output=True,
        check=True,
    )
    text = result.stdout.decode("utf-8-sig").replace("\r\n", "\n")

    def seconds(value):
        h, m, s = value.replace(",", ".").split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)

    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        start, end = lines[1].split(" --> ")
        cues.append(
            {
                "start": seconds(start),
                "end": seconds(end),
                "text": " ".join(
                    html.unescape(re.sub(r"<[^>]*>", "", " ".join(lines[2:]))).split()
                ),
            }
        )
    provided = read(ROOT / "video_course/r21/captions.json")
    assert len(cues) == len(provided)
    for embedded, expected in zip(cues, provided, strict=True):
        assert embedded["text"] == expected["text"]
        assert (
            abs(embedded["start"] - expected["start"]) < 0.003
            and abs(embedded["end"] - expected["end"]) < 0.003
        )
    return cues


ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Brand,Segoe UI,23,&H00FFFFFF,&H00FFFFFF,&H00172910,&H00172910,-1,0,0,0,100,100,0,0,3,12,0,7,24,24,14,1
Style: Context,Segoe UI,21,&H00A7F3D0,&H00FFFFFF,&H00172910,&H00172910,0,0,0,0,100,100,0,0,3,10,0,9,24,24,14,1
Style: Note,Segoe UI,25,&H00FFFFFF,&H00FFFFFF,&H00352212,&H00352212,-1,0,0,0,100,100,0,0,3,12,0,2,55,55,110,1
Style: Caption,Segoe UI,34,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,2,0,2,65,65,22,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def balanced(text):
    words = text.split()
    if len(text) <= 53:
        return text
    at = min(
        range(1, len(words)), key=lambda n: abs(len(" ".join(words[:n])) - len(" ".join(words[n:])))
    )
    return " ".join(words[:at]) + "\n" + " ".join(words[at:])


def caption_ass(cues, path):
    events = [
        f"Dialogue:0,{ass_time(c['start'])},{ass_time(c['end'])},Caption,,0,0,0,,{esc(balanced(c['text']))}"
        for c in cues
    ]
    path.write_text(ASS_HEADER + "\n".join(events) + "\n", encoding="utf-8")


def camera(receipt, duration):
    rect = receipt["proof"].get("focus_rect")
    action = receipt["action"]
    maximum = 1.38 if action.startswith(("code:", "write:", "focus_code:")) else 1.18
    if action.startswith("report"):
        maximum, rect = 1.2, [0, 120, 1000, 500]
    if action.startswith(("codegen", "trace", "debug")) or not rect:
        maximum = 1.0
    x, y, w, h = rect or [0, 0, 1920, 1080]
    # Keep the entire actual target, including long assertion endings, in view.
    maximum = max(1.0, min(maximum, 1920 / (w + 100), 1080 / (h + 80)))
    cw, ch = 1920 / maximum, 1080 / maximum
    fx = min(1, max(0, (x + w / 2 - cw / 2) / max(1, 1920 - cw)))
    fy = min(1, max(0, (y + h / 2 - ch / 2) / max(1, 1080 - ch)))
    start = max(0.5, receipt["action_finished"] + 0.15)
    if duration < start + 6.0:
        path = [{"t": 0, "zoom": 1.0}]
    else:
        path = [
            {"t": 0, "zoom": 1.0},
            {"t": start, "zoom": 1.0},
            {"t": start + 2.4, "zoom": maximum},
            {"t": duration - 2.6, "zoom": maximum},
            {"t": duration - 0.2, "zoom": 1.0},
        ]
    return {
        "keyframes": path,
        "fx": fx,
        "fy": fy,
        "actual_subject_rect": rect,
        "purpose": receipt["expected_visible_state"],
        "ease_seconds": 2.4,
        "camera_motion_counts_as_activity": False,
    }


def chapter(number):
    folder = HERE / "chapters" / f"{number:02}"
    out, rendered = folder / "output", folder / "rendered"
    out.mkdir(exist_ok=True)
    rendered.mkdir(exist_ok=True)
    contract_path = folder / "capture_contract.json"
    contract = read(contract_path)
    for name, digest in contract["inputs_sha256"].items():
        if sha(ROOT / name) != digest:
            raise ValueError(f"Capture input changed: {name}")
    receipts, plan = read(folder / "capture.json"), read(folder / "timeline.json")
    beats = read(folder / "beats.json")
    assert len(receipts) == len(beats)
    contract_sha = sha(contract_path)
    with wave.open(str(folder / "narration.wav")) as source:
        assert (source.getnchannels(), source.getsampwidth(), source.getframerate()) == (
            1,
            2,
            48000,
        )
        pcm = source.readframes(source.getnframes())
    expected_sample = 0
    for receipt, beat in zip(receipts, beats, strict=True):
        assert all(
            receipt[k] == beat[k]
            for k in (
                "id",
                "sample_start",
                "sample_end",
                "voice_cue",
                "expected_visible_state",
            )
        )
        assert receipt.get("original_planned_action", receipt["action"]) == beat["action"]
        assert (
            receipt["sample_start"] == expected_sample and receipt["sample_end"] > expected_sample
        )
        expected_sample = receipt["sample_end"]
    assert expected_sample * 2 == len(pcm)
    parts, shots, offset = [], [], 0.0
    for index, receipt in enumerate(receipts):
        receipt_contract = contract
        receipt_contract_sha = contract_sha
        if receipt.get("contract_path"):
            pickup_path = ROOT / receipt["contract_path"]
            receipt_contract, receipt_contract_sha = read(pickup_path), sha(pickup_path)
            assert receipt_contract["parent_contract_sha256"] == contract_sha
            for name, digest in receipt_contract["inputs_sha256"].items():
                assert sha(ROOT / name) == digest
            parent = ROOT / receipt["parent_receipt_path"]
            assert sha(parent) == receipt["parent_receipt_sha256"]
            original_receipt = read(parent)
            assert original_receipt["contract_sha256"] == contract_sha
            assert all(
                original_receipt[k] == receipt[k] for k in ("id", "sample_start", "sample_end")
            )
            assert original_receipt["action"] == receipt.get(
                "original_planned_action", receipt["action"]
            )
            if receipt.get("original_planned_action"):
                assert receipt_contract["semantic_override"] == {
                    "from": receipt["original_planned_action"],
                    "to": receipt["action"],
                }
        assert (
            receipt["contract_sha256"] == receipt_contract_sha
            and receipt["take"] == receipt_contract["take"]
        )
        clip = ROOT / receipt["clip"]
        assert sha(clip) == receipt["clip_sha256"]
        source_clip = clip
        visual = dict(receipt)
        wait_edit = None
        if receipt["action"].startswith("run:") and receipt["action_finished"] > max(
            12, receipt["duration"] + 2
        ):
            # Preserve the command and the final result at original speed. Only
            # the intervening actual test execution is visibly accelerated.
            short = receipt["duration"] < 10
            left, right = (
                (1.8 if short else 3.0),
                receipt["action_finished"] - (1.8 if short else 3.0),
            )
            middle_budget = max(
                0.0, receipt["duration"] - left - (receipt["action_finished"] - right) - 0.6
            )
            speed = (right - left) / middle_budget if middle_budget > 0.7 else None

            def local(at, left=left, right=right, speed=speed):
                return (
                    at
                    if at <= left
                    else left
                    + ((min(at, right) - left) / speed if speed else 0)
                    + max(0, at - right)
                )

            compressed = rendered / (receipt["id"] + "_wait_edit.mp4")
            edit_key = sha(clip) + str([left, right, speed])
            key_path = compressed.with_suffix(".key")
            if not cache_hit(compressed, key_path, edit_key):
                graph = (
                    f"[0:v]split=3[a][b][c];[a]trim=end={left},setpts=PTS-STARTPTS[x];"
                    f"[b]trim=start={left}:end={right},setpts=(PTS-STARTPTS)/{speed}[y];"
                    f"[c]trim=start={right},setpts=PTS-STARTPTS[z];[x][y][z]concat=n=3:v=1:a=0,fps=25[v]"
                )
                if speed is None:
                    graph = (
                        f"[0:v]split=2[a][b];[a]trim=end={left},setpts=PTS-STARTPTS[x];"
                        f"[b]trim=start={right},setpts=PTS-STARTPTS[y];[x][y]concat=n=2:v=1:a=0,fps=25[v]"
                    )
                run(
                    [
                        "-i",
                        str(clip),
                        "-filter_complex",
                        graph,
                        "-map",
                        "[v]",
                        "-an",
                        "-c:v",
                        "libx264",
                        "-preset",
                        "veryfast",
                        "-threads",
                        "4",
                        "-crf",
                        "18",
                        compressed.name,
                    ],
                    compressed.with_suffix(".log"),
                    rendered,
                )
                cache_save(compressed, key_path, edit_key)
            clip = compressed
            visual["action_finished"] = local(receipt["action_finished"])
            wait_edit = {
                "source_interval": [left, right],
                "speed": speed,
                "source_clip": str(source_clip.relative_to(ROOT)),
                "edited_sha256": sha(compressed),
                "disclosure": "Čekání na skutečný běh je zkrácené; příkaz a výsledek jsou v původní rychlosti.",
            }
        duration = math.ceil(max(receipt["duration"], visual["action_finished"] + 0.6) * 25) / 25
        piece = pcm[receipt["sample_start"] * 2 : receipt["sample_end"] * 2]
        target = round(duration * 48000)
        pad_samples = target - len(piece) // 2
        assert pad_samples >= 0
        if pad_samples > 2400 and index + 1 < len(receipts):
            import numpy as np

            seam = np.frombuffer(
                pcm[max(0, receipt["sample_end"] - 120) * 2 : (receipt["sample_end"] + 120) * 2],
                "<i2",
            )
            if max(abs(int(v)) for v in seam) >= 190:
                raise ValueError(f"Unsafe voiced boundary for a task wait: {receipt['id']}")
        parts.append(piece + b"\0" * (pad_samples * 2))
        rect, focus_detection = source_focus(receipt, folder)
        visual["proof"] = {**receipt["proof"], "focus_rect": rect}
        cam = camera(visual, duration)
        note = receipt["expected_visible_state"]
        style = rendered / f"{receipt['id']}.ass"
        end = ass_time(duration)
        events = [
            f"Dialogue:0,0:00:00.00,{end},Brand,,0,0,0,,PLAYWRIGHT ACADEMY / {esc(plan['title'].upper())}",
            f"Dialogue:0,0:00:00.00,{end},Context,,0,0,0,,KAPITOLA {number:02} / 12",
            f"Dialogue:0,0:00:00.00,{end},Note,,0,0,0,,{esc(note)}",
        ]
        if wait_edit:
            events.append(
                f"Dialogue:1,0:00:00.00,{end},Context,,0,0,0,,ČEKÁNÍ NA BĚH ZKRÁCENO / SKUTEČNÝ VÝSLEDEK"
            )
        style.write_text(ASS_HEADER + "\n".join(events) + "\n", encoding="utf-8")
        annotation = ""
        if receipt["action"] == "codegen_record":
            annotation = "drawbox=x=1090:y=0:w=22:h=ih:color=0x101b2c:t=fill,"
        rect = cam["actual_subject_rect"]
        if rect and receipt["action"].startswith(("code:", "write:", "focus_code:")):
            x, y, w, h = [round(v) for v in rect]
            annotation += (
                f"drawbox=x={x}:y={y}:w={w}:h={h}:color=0x67d59e@0.85:t=2:"
                f"enable='gte(t,{receipt['action_finished']:.3f})',"
            )
        filters = (
            annotation + f"tpad=stop_mode=clone:stop_duration={duration},"
            f"zoompan=z='{expression(cam['keyframes'])}':x='(iw-iw/zoom)*{cam['fx']}':y='(ih-ih/zoom)*{cam['fy']}':d=1:s=1920x1080:fps=25,"
            "scale=1920:926:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:0,"
            "drawbox=x=0:y=0:w=iw:h=58:color=0x10291e:t=fill,"
            "drawbox=x=0:y=926:w=iw:h=154:color=0x101b2c:t=fill,"
            f"ass={style.name}"
        )
        target_clip = rendered / (receipt["id"] + ".mp4")
        render_key = sha(clip) + sha(style) + json.dumps([filters, duration])
        key_file = target_clip.with_suffix(".key")
        if not cache_hit(target_clip, key_file, render_key):
            run(
                [
                    "-i",
                    str(clip),
                    "-vf",
                    filters,
                    "-t",
                    str(duration),
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-threads",
                    "4",
                    "-crf",
                    "19",
                    "-pix_fmt",
                    "yuv420p",
                    target_clip.name,
                ],
                target_clip.with_suffix(".log"),
                rendered,
            )
            cache_save(target_clip, key_file, render_key)
        shots.append(
            {
                **receipt,
                "planned_start": receipt["start"],
                "planned_end": receipt["end"],
                "start": offset,
                "end": offset + duration,
                "duration": duration,
                "camera": cam,
                "focus_detection": focus_detection,
                "audio_tail_padding_samples": pad_samples,
                "wait_edit": wait_edit,
                "real_action_interval": [
                    offset + receipt["action_started"],
                    offset + visual["action_finished"],
                ],
                "verified_final_state_hold_seconds": max(0, duration - visual["action_finished"]),
                "hold_reason": "Výklad právě ukázaného stavu a jeho ověření; nová aktivita se nedeklaruje.",
            }
        )
        offset = round(offset + duration, 6)
        print(json.dumps({"rendered": receipt["id"], "duration": duration}), flush=True)

    def mapped(at, ending=False):
        for shot in shots:
            if (
                shot["planned_start"] <= at < shot["planned_end"]
                or ending
                and abs(at - shot["planned_end"]) < 1e-7
            ):
                return shot["start"] + at - shot["planned_start"]
        return offset

    words = []
    for section in plan["sections"]:
        # Native word events can split a filename at a dot. Rejoin against the
        # exact canonical tokens, retaining the union of their real boundaries.
        native, cursor = [], 0
        for word in section["words"]:
            text = re.sub(r"\s+", "", word["text"])
            native.append((cursor, cursor + len(text), word))
            cursor += len(text)
        assert "".join(re.sub(r"\s+", "", w["text"]) for w in section["words"]) == re.sub(
            r"\s+", "", section["paragraph"]
        )
        cursor = 0
        for token in section["paragraph"].split():
            right = cursor + len(token)
            overlapping = [
                (left, end, w) for left, end, w in native if left < right and end > cursor
            ]
            left, end, first_word = overlapping[0]
            first_time = first_word["start"] + (first_word["end"] - first_word["start"]) * max(
                0, cursor - left
            ) / max(1, end - left)
            left, end, last_word = overlapping[-1]
            last_time = last_word["start"] + (last_word["end"] - last_word["start"]) * min(
                end - left, right - left
            ) / max(1, end - left)
            words.append(
                {
                    "text": token,
                    "start": mapped(first_time),
                    "end": mapped(last_time, True),
                }
            )
            cursor = right
    transcript = " ".join(section["paragraph"] for section in plan["sections"])
    cues = audio.captions(transcript, words, [])
    assert all(a["end"] <= b["start"] + 0.001 for a, b in zip(cues, cues[1:], strict=False))
    write_captions(cues, out / "subtitles_cs")
    save(out / "captions.json", cues)
    save(out / "caption_word_map.json", words)
    with wave.open(str(out / "narration.wav"), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(48000)
        for piece in parts:
            stream.writeframes(piece)
    playlist = "ffconcat version 1.0\n" + "".join(
        f"file '../rendered/{s['id']}.mp4'\n" for s in shots
    )
    (out / "edit.ffconcat").write_text(playlist, encoding="utf-8")
    movie = out / f"chapter_{number:02}.mp4"
    run(
        [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "edit.ffconcat",
            "-i",
            "narration.wav",
            "-i",
            "subtitles_cs.srt",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-map",
            "2:0",
            "-c:v",
            "copy",
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-c:s",
            "mov_text",
            "-metadata:s:s:0",
            "language=ces",
            "-t",
            str(offset),
            "-movflags",
            "+faststart",
            movie.name,
        ],
        out / "mux.log",
        out,
    )
    save(
        out / "edit_project.json",
        {
            "chapter": number,
            "title": plan["title"],
            "learning_outcome": plan["learning_outcome"],
            "duration": offset,
            "voice": "cs-CZ-VlastaNeural",
            "caption_alignment": "Native word intervals with canonical-token joining and proportional splitting only within a shared native token",
            "shots": shots,
            "human_watch_and_listen": "PENDING_FULL_COURSE_REVIEW",
            "movie_sha256": sha(movie),
            "input_contract_sha256": contract_sha,
            "sidecars_sha256": {
                p.name: sha(p)
                for p in [
                    out / "captions.json",
                    out / "subtitles_cs.srt",
                    out / "subtitles_cs.vtt",
                    out / "narration.wav",
                    out / "caption_word_map.json",
                ]
            },
        },
    )
    return movie


def assemble():
    out = HERE / "output"
    out.mkdir(exist_ok=True)
    manifest = read(HERE / "course_manifest.json")
    approval = read(ROOT / "video_course/r21/po_approval.json")
    chapters, cues, movies, offset = [], [], [], 0.0
    transcript_paragraphs = []
    for entry in manifest["chapters"]:
        n = entry["chapter"]
        if n == 4:
            folder = ROOT / "video_course/r21/output"
            movie = folder / "Playwright_Academy_R21_Prvni_Test.mp4"
            assert sha(movie) == approval["movies"][movie.name]
            local_cues = approved_reference_captions(movie)
            duration = 348.48
        else:
            folder = HERE / "chapters" / f"{n:02}" / "output"
            project = read(folder / "edit_project.json")
            for name, digest in project["sidecars_sha256"].items():
                assert sha(folder / name) == digest
            movie = folder / f"chapter_{n:02}.mp4"
            assert sha(movie) == project["movie_sha256"]
            duration, local_cues = project["duration"], read(folder / "captions.json")
        movies.append(movie)
        paragraph_plan = (
            ROOT / "video_course/r21/timeline.json"
            if n == 4
            else HERE / "chapters" / f"{n:02}" / "timeline.json"
        )
        transcript_paragraphs.extend(s["paragraph"] for s in read(paragraph_plan)["sections"])
        chapters.append(
            {
                **entry,
                "status": "APPROVED_REFERENCE_REUSED"
                if n == 4
                else "RENDERED_AWAITING_OWNER_REVIEW",
                "start": offset,
                "end": offset + duration,
                "duration": duration,
                "source_sha256": sha(movie),
            }
        )
        cues.extend(
            {**c, "start": c["start"] + offset, "end": c["end"] + offset} for c in local_cues
        )
        offset = round(offset + duration, 6)
    previous_end = 0
    for cue in cues:
        assert 0 <= cue["start"] < cue["end"] <= offset
        assert cue["start"] >= previous_end - 0.003
        previous_end = cue["end"]
        assert len(balanced(cue["text"]).splitlines()) <= 2
    write_captions(cues, out / "subtitles_cs")
    caption_ass(cues, out / "caption_overlay.ass")
    save(out / "captions.json", cues)
    save(out / "chapters.json", chapters)
    (out / "transcript_cs.txt").write_text(
        "\n\n".join(transcript_paragraphs) + "\n", encoding="utf-8"
    )
    assert " ".join(" ".join(transcript_paragraphs).split()) == " ".join(c["text"] for c in cues)
    meta = ";FFMETADATA1\ntitle=Playwright Academy — Python\n"
    for c in chapters:
        meta += f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(c['start'] * 1000)}\nEND={round(c['end'] * 1000)}\ntitle={c['title']}\n"
    (out / "chapters.ffmeta").write_text(meta, encoding="utf-8")
    # Stream-copy the actual approved and newly edited pictures. Re-encode audio
    # once to avoid per-chapter AAC priming offsets. Global captions are remuxed.
    (out / "course.ffconcat").write_text(
        "ffconcat version 1.0\n"
        + "".join(
            f"file '{p.as_posix()}'\nduration {c['duration']:.6f}\n"
            for p, c in zip(movies, chapters, strict=True)
        ),
        encoding="utf-8",
    )
    # Decode each chapter's already level-matched narration with its AAC edit
    # list, then join exact sample counts. Per-file AAC priming must not shift
    # later chapter boundaries or the canonical global subtitles.
    with wave.open(str(out / "course_audio.wav"), "wb") as joined:
        joined.setnchannels(1)
        joined.setsampwidth(2)
        joined.setframerate(48000)
        for p, c in zip(movies, chapters, strict=True):
            decoded = out / f"audio_{c['chapter']:02}.wav"
            count = round(c["duration"] * 48000)
            run(
                [
                    "-i",
                    str(p),
                    "-map",
                    "0:a:0",
                    "-af",
                    f"apad,atrim=end_sample={count}",
                    "-ar",
                    "48000",
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    decoded.name,
                ],
                decoded.with_suffix(".log"),
                out,
            )
            with wave.open(str(decoded)) as stream:
                assert stream.getnframes() == count
                joined.writeframes(stream.readframes(count))
    movie = out / "Playwright_Academy_Python_CZ_Full_Course.mp4"
    run(
        [
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "course.ffconcat",
            "-i",
            "course_audio.wav",
            "-i",
            "subtitles_cs.srt",
            "-i",
            "chapters.ffmeta",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-map",
            "2:0",
            "-map_metadata",
            "3",
            "-map_chapters",
            "3",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-c:s",
            "mov_text",
            "-metadata:s:s:0",
            "language=ces",
            "-metadata:s:s:0",
            "title=Čeština",
            "-t",
            str(offset),
            "-movflags",
            "+faststart",
            movie.name,
        ],
        out / "mux.log",
        out,
    )
    burned = out / "Playwright_Academy_Python_CZ_Full_Course_Titulky.mp4"
    run(
        [
            "-i",
            movie.name,
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-vf",
            "ass=caption_overlay.ass",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-threads",
            "4",
            "-crf",
            "19",
            "-c:a",
            "copy",
            "-map_metadata",
            "0",
            "-map_chapters",
            "0",
            "-movflags",
            "+faststart",
            burned.name,
        ],
        out / "burn.log",
        out,
    )
    for p in (movie, burned):
        run(
            ["-v", "error", "-i", p.name, "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"],
            p.with_suffix(".decode.log"),
            out,
        )
        assert p.with_suffix(".decode.log").stat().st_size == 0
    save(
        out / "validation.json",
        {
            "duration": offset,
            "chapters": len(chapters),
            "captions": len(cues),
            "movies": {p.name: sha(p) for p in (movie, burned)},
            "voice": "cs-CZ-VlastaNeural",
            "reference_approved": True,
            "full_course_human_review": "PENDING",
            "decode_errors": 0,
        },
    )
    save(
        out / "edit_project.json",
        {
            "revision": "FULL_R21_STANDARD",
            "status": "READY_FOR_OWNER_REVIEW",
            "duration": offset,
            "voice": "cs-CZ-VlastaNeural",
            "frozen_commit": approval["frozen_commit"],
            "chapters": [
                {
                    **c,
                    "edit_project": (
                        "video_course/r21/output/edit_project.json"
                        if c["chapter"] == 4
                        else f"video_course/full/chapters/{c['chapter']:02}/output/edit_project.json"
                    ),
                }
                for c in chapters
            ],
            "captions": cues,
            "movies": {p.name: sha(p) for p in (movie, burned)},
            "sidecars_sha256": {
                p.name: sha(p)
                for p in (
                    out / "subtitles_cs.srt",
                    out / "subtitles_cs.vtt",
                    out / "captions.json",
                    out / "chapters.json",
                )
            },
            "rebuild": "python video_course/full/build.py --assemble",
            "owner_reference_approval": "APPROVED",
            "whole_course_human_acceptance": "PENDING",
        },
    )
    save(
        HERE / "course_manifest.json",
        {
            **manifest,
            "chapters": chapters,
            "duration": offset,
            "production_status": "READY_FOR_OWNER_REVIEW",
            "whole_course_human_acceptance": "PENDING",
        },
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapters", type=int, nargs="+")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()
    selected = args.chapters or [n for n in range(1, 13) if n != 4]
    for n in selected:
        capture = HERE / "chapters" / f"{n:02}" / "capture.json"
        while not capture.exists():
            if not args.watch:
                raise FileNotFoundError(capture)
            if (HERE / "stop.request").exists():
                raise RuntimeError("Owner stop request")
            time.sleep(5)
        chapter(n)
    if args.assemble:
        assemble()


if __name__ == "__main__":
    main()
