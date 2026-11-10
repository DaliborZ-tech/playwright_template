"""Retiming verified real captures to narration; every parent receipt remains immutable."""

import json
import subprocess

from media import ffmpeg
from prepare import HERE, OLD, ROOT, read, save, sha


def main():
    timeline = read(HERE / "timeline.json")
    old_receipts = read(OLD / "capture.json")
    cg_receipts = read(HERE / "codegen_capture.json")
    parents = {r["id"]: r for r in old_receipts + cg_receipts}
    # Preserve the original capture contract before creating an edit contract.
    cg_contract = HERE / "codegen_capture_contract.json"
    current_contract = HERE / "capture_contract.json"
    if not cg_contract.exists():
        cg_contract.write_bytes(current_contract.read_bytes())
    inputs = [
        HERE / n
        for n in (
            "timeline.json",
            "captions.json",
            "narration.wav",
            "audio_edits.json",
            "codegen_capture.json",
            "codegen_capture_contract.json",
        )
    ]
    inputs += [OLD / "capture.json", OLD / "capture_contract.json", OLD / "reference.json"]
    inputs += [ROOT / r["clip"] for r in parents.values()]
    for section in read(OLD / "timeline.json")["sections"]:
        audio = ROOT / section["audio"]
        inputs.extend((audio, audio.with_suffix(".json")))
    inputs.extend((OLD / "narration.wav", ROOT / read(HERE / "codegen_narration.json")["audio"]))
    contract = {
        "revision": "R2.1",
        "run_group": "r21_verified_capture_edit",
        "voice": "cs-CZ-VlastaNeural",
        "inputs_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs},
    }
    save(current_contract, contract)
    result = []
    target_dir = HERE / "edited"
    target_dir.mkdir(exist_ok=True)
    for shot in timeline["shots"]:
        parent = parents[shot["id"]]
        source = ROOT / parent["clip"]
        assert sha(source) == parent["clip_sha256"]
        duration = shot["duration"]
        s, e, total = parent["action_started"], parent["action_finished"], parent["actual_duration"]
        ns = min(max(0.35, shot["action_offset"]), duration - 0.5)
        ne = ns + min(max(e - s, 0.02), duration - ns - 0.20)
        pre = ns / max(s, 0.001)
        active = (ne - ns) / max(e - s, 0.001)
        post = (duration - ne) / max(total - e, 0.001)
        expression = (
            f"if(lt(PTS*TB,{s:.6f}),PTS*TB*{pre:.8f},"
            f"if(lt(PTS*TB,{e:.6f}),{ns:.6f}+(PTS*TB-{s:.6f})*{active:.8f},"
            f"{ne:.6f}+(PTS*TB-{e:.6f})*{post:.8f}))/TB"
        )
        destination = target_dir / (shot["id"] + ".mp4")
        subprocess.run(
            [
                ffmpeg(),
                "-y",
                "-v",
                "error",
                "-i",
                str(source),
                "-vf",
                f"setpts='{expression}',fps=25,tpad=stop_mode=clone:stop_duration=0.1",
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
                "18",
                "-pix_fmt",
                "yuv420p",
                str(destination),
            ],
            check=True,
        )
        receipt = {
            **shot,
            "status": "edited_from_real_capture",
            "human_review": "pending",
            "run_group": contract["run_group"],
            "contract_sha256": sha(current_contract),
            "action_started": ns,
            "action_finished": ne,
            "actual_duration": duration,
            "clip": str(destination.relative_to(ROOT)),
            "clip_sha256": sha(destination),
            "capture_method": "retimed_verified_real_capture",
            "proof": parent["proof"],
            "parent_clip": parent["clip"],
            "parent_clip_sha256": parent["clip_sha256"],
            "parent_contract_sha256": parent["contract_sha256"],
            "parent_capture_method": parent["capture_method"],
            "retiming_control_points": [[0, 0], [s, ns], [e, ne], [total, duration]],
            "active_speed_factor": round(1 / active, 6) if e > s else 1,
            "note": "Real actions retained; waiting/holding time edited. No UI states fabricated.",
        }
        save(destination.with_suffix(".json"), receipt)
        result.append(receipt)
        print(json.dumps({"edited": shot["id"], "seconds": duration}), flush=True)
    save(HERE / "capture.json", result)


if __name__ == "__main__":
    main()
