"""Capture every authored semantic action in owned real applications, with provenance."""

import argparse
import json
import math
import os
import subprocess
import time
import wave
from collections import deque
from threading import Event, Thread

from prepare import HERE, ROOT, audio
from session import Session, sha, win32gui
from studio import ffmpeg, owns_foreground

PRODUCER_SOURCES = {
    p: (ROOT / p).read_bytes()
    for p in (
        "video_course/full/capture.py",
        "video_course/full/session.py",
        "video_course/production/studio.py",
        "video_course/production/open_studio.py",
        "video_course/production/record_course.py",
        "video_course/full/open_trace.cjs",
    )
}


def owned_process(handle, session):
    if any(owns_foreground(h) for h in session.handles if win32gui.IsWindow(h)):
        return True
    import psutil
    import win32process

    roots = {os.getpid()}
    roots.update(
        win32process.GetWindowThreadProcessId(h)[1] for h in session.handles if win32gui.IsWindow(h)
    )
    try:
        pid = win32process.GetWindowThreadProcessId(handle)[1]
        return pid in roots or any(p.pid in roots for p in psutil.Process(pid).parents())
    except (psutil.Error, RuntimeError):
        return False


def build_beats(plan, samples):
    events = [e for section in plan["sections"] for e in section["narration_action_cues"]]
    events.sort(key=lambda e: e["time"])
    cuts = [0]
    for event in events[1:]:
        at = event["time"]
        point = max(cuts[-1] + 1, math.floor((at - 0.025) * 48000))
        # Find a genuinely quiet seam before the native first word. This allows
        # occasional real task pauses without splitting a spoken phoneme.
        for sample in range(point, max(cuts[-1], point - 9600), -48):
            if max(abs(int(v)) for v in samples[max(0, sample - 120) : sample + 120]) < 190:
                point = sample
                break
        cuts.append(point)
    cuts.append(len(samples))
    return [
        {
            **event,
            "id": f"{plan['chapter']:02}_{i:03}",
            "sample_start": cuts[i],
            "sample_end": cuts[i + 1],
            "start": cuts[i] / 48000,
            "end": cuts[i + 1] / 48000,
            "duration": (cuts[i + 1] - cuts[i]) / 48000,
        }
        for i, event in enumerate(events)
    ]


def capture(session, beat, contract):
    folder = session.stage / "raw" / session.take
    folder.mkdir(parents=True, exist_ok=True)
    clip = folder / (beat["id"] + ".mp4")
    log_path = clip.with_suffix(".log")
    command = [
        ffmpeg(),
        "-y",
        "-hide_banner",
        "-v",
        "error",
        "-f",
        "gdigrab",
        "-framerate",
        "25",
        "-draw_mouse",
        "1",
        "-offset_x",
        "0",
        "-offset_y",
        "0",
        "-video_size",
        "1920x1032",
        "-i",
        "desktop",
        "-vf",
        "pad=1920:1080:0:24",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-tune",
        "zerolatency",
        "-threads",
        "4",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-progress",
        "pipe:1",
        "-stats_period",
        "0.1",
        str(clip),
    ]
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log, text=True
        )
        started = time.monotonic()
        try:
            while True:
                line = process.stdout.readline()
                if not line:
                    raise RuntimeError("Recorder exited before its first actual frame")
                if line.startswith("frame=") and int(line.split("=")[1]) > 0:
                    first_frame = time.monotonic()
                    break
            drain = Thread(target=lambda: deque(process.stdout, maxlen=1), daemon=True)
            drain.start()
            guard_stop, foreign = Event(), []

            def guard():
                while not guard_stop.wait(0.05):
                    handle = win32gui.GetForegroundWindow()
                    if handle and not owned_process(handle, session):
                        foreign.append({"handle": handle, "at": time.monotonic() - started})

            watchdog = Thread(target=guard, daemon=True)
            watchdog.start()
            action_start = time.monotonic() - started
            proof = session.act(beat["action"])
            action_end = time.monotonic() - started
            time.sleep(0.8)
            if not any(owns_foreground(h) for h in session.handles if win32gui.IsWindow(h)):
                raise RuntimeError("Foreign foreground window; real capture rejected")
            if foreign:
                raise RuntimeError(f"Foreign window during action; capture rejected: {foreign}")
            process.stdin.write("q\n")
            process.stdin.flush()
            process.wait(timeout=20)
            drain.join(timeout=2)
        finally:
            if "guard_stop" in locals():
                guard_stop.set()
                watchdog.join(timeout=2)
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
    if process.returncode:
        raise RuntimeError(f"Recorder failed: {beat['id']}")
    result = {
        **beat,
        "chapter": session.chapter,
        "take": session.take,
        "status": "REAL_ACTION_CAPTURED",
        "clip": str(clip.relative_to(ROOT)),
        "clip_sha256": sha(clip),
        "contract_sha256": sha(contract),
        "action_started": action_start,
        "action_finished": action_end,
        "first_encoded_frame_wall_offset": first_frame - started,
        "capture_method": "actual_owned_editor_browser_terminal_desktop",
        "foreground_guard_poll_seconds": 0.05,
        "proof": proof,
        "human_review": "pending",
    }
    audio.save(clip.with_suffix(".json"), result)
    print(
        json.dumps(
            {
                "chapter": session.chapter,
                "beat": beat["id"],
                "action": beat["action"],
                "captured_seconds": round(action_end + 0.8, 2),
            }
        ),
        flush=True,
    )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--chapters", type=int, nargs="+", default=[n for n in range(1, 13) if n != 4]
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    for chapter in args.chapters:
        if chapter == 4:
            continue
        stage = HERE / "chapters" / f"{chapter:02}"
        plan = audio.read(stage / "timeline.json")
        contract = stage / "capture_contract.json"
        input_hashes = {
            str(p.relative_to(ROOT)): sha(p)
            for p in (
                stage / "timeline.json",
                stage / "narration.wav",
                ROOT / "video_course/r21/po_approval.json",
            )
        }
        if args.resume and (stage / "capture.json").exists() and contract.exists():
            previous = audio.read(contract)
            receipts = audio.read(stage / "capture.json")
            if (
                all(
                    previous["inputs_sha256"].get(name) == digest
                    for name, digest in input_hashes.items()
                )
                and all(
                    (ROOT / name).exists() and sha(ROOT / name) == digest
                    for name, digest in previous["inputs_sha256"].items()
                )
                and all(sha(ROOT / r["clip"]) == r["clip_sha256"] for r in receipts)
            ):
                print(
                    json.dumps({"chapter": chapter, "status": "VERIFIED_COMPLETE_CAPTURE_REUSED"}),
                    flush=True,
                )
                continue
        with wave.open(str(stage / "narration.wav")) as stream:
            import numpy as np

            samples = np.frombuffer(stream.readframes(stream.getnframes()), "<i2")
        beats = build_beats(plan, samples)
        audio.save(stage / "beats.json", beats)
        session = Session(chapter)
        input_hashes[str((stage / "beats.json").relative_to(ROOT))] = sha(stage / "beats.json")
        for name, content in PRODUCER_SOURCES.items():
            snapshot = stage / "source_versions" / session.take / name
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(content)
            input_hashes[str(snapshot.relative_to(ROOT))] = sha(snapshot)
        audio.save(
            contract,
            {
                "inputs_sha256": input_hashes,
                "take": session.take,
                "voice": "cs-CZ-VlastaNeural",
                "frozen_commit": plan["frozen_commit"],
            },
        )
        result = []
        try:
            for beat in beats:
                if (HERE / "stop.request").exists():
                    reason = (HERE / "stop.request").read_text(encoding="utf-8-sig").strip()
                    raise RuntimeError(f"Recording stop request: {reason}")
                if args.preflight:
                    proof = session.act(beat["action"])
                    result.append({**beat, "proof": proof})
                    print(
                        json.dumps({"preflight": beat["id"], "action": beat["action"]}), flush=True
                    )
                else:
                    result.append(capture(session, beat, contract))
                    audio.save(stage / "capture_progress.json", result)
        finally:
            session.close()
        audio.save(stage / ("preflight.json" if args.preflight else "capture.json"), result)


if __name__ == "__main__":
    main()
