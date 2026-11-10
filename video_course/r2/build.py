"""Render the gated reference chapter, semantic overlays and both subtitle variants."""
# ASS style tables are serialized data; each style must occupy one physical line.
# ruff: noqa: E501

import argparse
import hashlib
import json
import math
import subprocess
import textwrap
import wave
from pathlib import Path

from media import ffmpeg, timestamp, write_captions

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(args, log):
    with log.open("w", encoding="utf-8") as stream:
        subprocess.run(
            [ffmpeg(), "-y", "-hide_banner", *args], stdout=stream, stderr=stream, check=True
        )


def ass_text(text):
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", r"\N")


def ass_time(seconds):
    return timestamp(seconds)[1:-1]


LABELS = {
    "browser": "ŽIVÁ APLIKACE",
    "editor": "VS CODE · tests/examples/test_video_created.py",
    "terminal": "SKUTEČNÝ BĚH PYTEST",
    "test_video": "BROWSER ZE SKUTEČNÉHO BĚHU",
}

NOTES = {
    "open_login": "Cíl: zobrazit formulář a ověřit dva prvky",
    "fill_email": "Syntetický účet · tester@example.test",
    "fill_clear": "Ruční průzkum před automatizací",
    "blank": "Začínáme od prázdného souboru",
    "type_import": "Page → karta prohlížeče    expect → očekávání",
    "type_function": "Vlastní funkce test_* a připravená fixture page",
    "type_goto": 'Navigace: page.goto("/login")',
    "save": "Uložit před spuštěním testu",
    "inspect_heading": "Živý DOM: h2 → role heading → Přihlášení",
    "type_heading": "Najít konkrétní nadpis a ověřit jeho viditelnost",
    "type_button": "Druhé očekávání: tlačítko Přihlásit se",
    "inspect_button": "Živý DOM: button a jeho skutečný text",
    "make_red": "Záměrná chyba: očekávaný text, který na stránce není",
    "red_command": "Spouštíme jediný konkrétní test",
    "red_run": "Běží skutečný pytest; pomalejší ukázka pro sledování",
    "red_video": "RED · záznam právě tohoto testu, nikoli simulace",
    "red_result": "RED · 1 failed · exit 1",
    "red_detail": "Příčina: Neexistující nadpis ≠ Přihlášení",
    "make_green": "Oprava jediné hodnoty; očekávání zůstává",
    "green_command": "Tentýž test · jiná složka pro uchování reportu",
    "green_run": "Opakovaný skutečný běh téhož případu",
    "green_video": "Záznam browseru z druhého běhu",
    "green_result": "GREEN · 1 passed · exit 0",
    "open_report": "Čerstvý HTML report úspěšného běhu",
    "report_details": "Název případu a výsledek patří k napsanému testu",
    "final_code": "Import → funkce → navigace → dvě očekávání",
    "exercise": "Vlastní úkol: doplňte kontrolu e-mailového pole",
}


def overlay(path, shot, index, duration):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Brand,Segoe UI,23,&H00FFFFFF,&H00FFFFFF,&H00172910,&H00172910,-1,0,0,0,100,100,0,0,3,12,0,7,24,24,14,1
Style: Context,Segoe UI,21,&H00A7F3D0,&H00FFFFFF,&H00172910,&H00172910,0,0,0,0,100,100,0,0,3,10,0,9,24,24,14,1
Style: Note,Segoe UI,25,&H00FFFFFF,&H00FFFFFF,&H00352212,&H00352212,-1,0,0,0,100,100,0,0,3,12,0,2,55,55,110,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    end = ass_time(duration)
    lines = [
        f"Dialogue:0,0:00:00.00,{end},Brand,,0,0,0,,PLAYWRIGHT ACADEMY  /  PRVNÍ TEST",
        f"Dialogue:0,0:00:00.00,{end},Context,,0,0,0,,{index:02}/27  ·  {LABELS[shot['view']]}",
        f"Dialogue:0,0:00:00.00,{end},Note,,0,0,0,,"
        + r"{\fad(120,180)}"
        + ass_text(NOTES[shot["on_screen_action"]]),
    ]
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", action="store_true")
    args = parser.parse_args()
    if args.package:
        from package import main as package_main

        package_main()
        return
    plan = read(HERE / "timeline.json")
    captures = read(HERE / "capture.json")
    contract = read(HERE / "capture_contract.json")
    for name, digest in contract["inputs_sha256"].items():
        if sha(ROOT / name) != digest:
            raise ValueError(f"Capture input changed; record again: {name}")
    out = HERE / "output"
    rendered = HERE / "rendered"
    out.mkdir(exist_ok=True)
    rendered.mkdir(exist_ok=True)
    with wave.open(str(HERE / "narration.wav")) as source:
        pcm = source.readframes(source.getnframes())
    parts, actual_shots, offset = [], [], 0.0
    for index, (shot, receipt) in enumerate(zip(plan["shots"], captures, strict=True), 1):
        if (
            receipt["contract_sha256"] != sha(HERE / "capture_contract.json")
            or receipt["run_group"] != contract["run_group"]
        ):
            raise ValueError("Recorded take belongs to a different capture contract")
        if receipt["id"] != shot["id"] or receipt["on_screen_action"] != shot["on_screen_action"]:
            raise ValueError("Recorded shot order/identity differs from the narration contract")
        clip = ROOT / receipt["clip"]
        assert sha(clip) == receipt["clip_sha256"]
        duration = shot["duration"]
        if index == len(captures):
            audio_end = math.ceil(len(pcm) / 96000 * 25) / 25
            duration = max(duration, round(audio_end - shot["start"], 3))
        if shot["view"] != "test_video" and receipt["action_finished"] > duration - 0.05:
            raise ValueError(f"Action overruns narration budget; rewrite/re-record {shot['id']}")
        sample_end = len(pcm) if index == len(captures) else round(shot["end"] * 48000) * 2
        piece = pcm[round(shot["start"] * 48000) * 2 : sample_end]
        target_samples = round(duration * 48000)
        # Never insert silence into a paragraph at an image edit. All pieces
        # rejoin without a gap; only the final sub-frame audio tail is padded.
        piece += b"\x00" * max(0, target_samples * 2 - len(piece))
        parts.append(piece[: target_samples * 2])
        maximum = 1.25 if shot["view"] == "editor" else 1.08
        fx, fy = 0.72, 0.15
        if shot["view"] == "terminal":
            maximum, fx, fy = 1.12, 0.7, 0.65
        if shot["on_screen_action"].startswith("inspect"):
            maximum, fx, fy = 1.48, 1.0, 0.18
        if shot["on_screen_action"] in {"open_report", "report_details"}:
            # Keep the real Result/Passed column and summary at the left edge.
            maximum, fx, fy = 1.35, 0.0, 0.0
        progress = "min(max((on-30)/25,0),1)"
        z = f"1+{maximum - 1:.4f}*({progress})*({progress})*(3-2*({progress}))"
        focus_line = {
            "type_import": 3,
            "type_function": 6,
            "type_goto": 7,
            "type_heading": 8,
            "type_button": 9,
            "make_red": 8,
            "make_green": 8,
            "final_code": 6,
        }.get(shot["on_screen_action"])
        annotation = ""
        if focus_line:
            height = 124 if shot["on_screen_action"] == "final_code" else 34
            annotation = (
                f"drawbox=x=432:y={90 + (focus_line - 1) * 30}:w=1110:h={height}:"
                "color=0x67d59e@0.85:t=2:"
                f"enable='gte(t,{receipt['action_finished']:.3f})',"
            )
        filters = (
            annotation + "tpad=stop_mode=clone:stop_duration=2,"
            f"zoompan=z='{z}':x='(iw-iw/zoom)*{fx}':y='(ih-ih/zoom)*{fy}'"
            ":d=1:s=1920x1080:fps=25,"
            "scale=1920:926:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:0,"
            "drawbox=x=0:y=0:w=iw:h=58:color=0x10291e:t=fill,"
            "drawbox=x=0:y=926:w=iw:h=154:color=0x101b2c:t=fill,"
            f"ass={shot['id']}.ass"
        )
        style = rendered / f"{shot['id']}.ass"
        overlay(style, shot, index, duration)
        output = rendered / f"{shot['id']}.mp4"
        command = [
            ffmpeg(),
            "-y",
            "-hide_banner",
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
            output.name,
        ]
        with output.with_suffix(".log").open("w", encoding="utf-8") as log:
            subprocess.run(command, cwd=rendered, stdout=log, stderr=log, check=True)
        actual_shots.append(
            {
                **shot,
                "planned_start": shot["start"],
                "planned_end": shot["end"],
                "start": offset,
                "end": offset + duration,
                "duration": duration,
                "camera": {
                    "zoom": maximum,
                    "target_x_fraction": fx,
                    "target_y_fraction": fy,
                    "ease_seconds": 1.0,
                    "purpose": shot["expected_visible_state"],
                    "code_focus_line": focus_line,
                },
                "actual_action_interval": [
                    offset + receipt["action_started"],
                    offset + receipt["action_finished"],
                ],
                "source_clip": receipt["clip"],
                "source_sha256": receipt["clip_sha256"],
                "proof": receipt["proof"],
            }
        )
        offset += duration
        print(json.dumps({"rendered_shot": shot["id"], "seconds": duration}), flush=True)
    if not 300 <= offset <= 480:
        raise ValueError("Only a5–8minute reference chapter may be rendered")
    with wave.open(str(out / "narration.wav"), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(48000)
        for piece in parts:
            stream.writeframes(piece)

    def actual_time(at):
        for shot in actual_shots:
            if shot["planned_start"] <= at < shot["planned_end"]:
                return shot["start"] + at - shot["planned_start"]
        return offset

    # Native caption words stay canonical; only explicitly recorded waiting gaps shift them.
    original = []
    for section in plan["sections"]:
        audio = ROOT / section["audio"]
        data = read(audio.with_suffix(".json"))
        original.extend(
            {**c, "start": section["start"] + c["start"], "end": section["start"] + c["end"]}
            for c in data["cues"]
        )
    cues = [{**c, "start": actual_time(c["start"]), "end": actual_time(c["end"])} for c in original]
    write_captions(cues, out / "subtitles_cs")
    playlist = "ffconcat version 1.0\n" + "".join(
        f"file '../rendered/{s['id']}.mp4'\n" for s in actual_shots
    )
    (out / "edit.ffconcat").write_text(playlist, encoding="utf-8")
    movie = out / "Playwright_Academy_R2_Prvni_Test.mp4"
    command = [
        ffmpeg(),
        "-y",
        "-hide_banner",
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
        "-metadata:s:s:0",
        "title=Čeština",
        "-movflags",
        "+faststart",
        "-t",
        str(offset),
        movie.name,
    ]
    with (out / "mux.log").open("w", encoding="utf-8") as log:
        subprocess.run(command, cwd=out, stdout=log, stderr=log, check=True)
    burned = out / "Playwright_Academy_R2_Prvni_Test_Titulky.mp4"
    caption_style = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Segoe UI,34,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,2,0,2,65,65,22,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for cue in cues:
        lines = "\n".join(textwrap.wrap(cue["text"], width=70, break_long_words=False))
        events.append(
            f"Dialogue:0,{ass_time(cue['start'])},{ass_time(cue['end'])},"
            "Caption,,0,0,0,," + ass_text(lines)
        )
    (out / "caption_overlay.ass").write_text(
        caption_style + "\n".join(events) + "\n", encoding="utf-8"
    )
    burn_filter = "ass=caption_overlay.ass"
    with (out / "burn.log").open("w", encoding="utf-8") as log:
        subprocess.run(
            [
                ffmpeg(),
                "-y",
                "-hide_banner",
                "-i",
                movie.name,
                "-map",
                "0:v:0",
                "-map",
                "0:a:0",
                "-vf",
                burn_filter,
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
                "-movflags",
                "+faststart",
                burned.name,
            ],
            cwd=out,
            stdout=log,
            stderr=log,
            check=True,
        )
    for video in (movie, burned):
        run(
            ["-v", "error", "-i", str(video), "-map", "0:v:0", "-map", "0:a:0", "-f", "null", "-"],
            video.with_suffix(".decode.log"),
        )
        assert video.with_suffix(".decode.log").stat().st_size == 0
    final = {
        "revision": "R2",
        "status": "READY_FOR_HUMAN_REVIEW",
        "human_watch_and_listen": "NOT_PERFORMED",
        "po_approval": "PENDING",
        "full_course_build_authorized": False,
        "title": plan["title"],
        "duration": offset,
        "voice": "cs-CZ-VlastaNeural",
        "shots": actual_shots,
        "narration_action_cues": [
            {
                "shot": shot["id"],
                "voice_cue": shot["voice_cue"],
                "voice_at": actual_time(shot["voice_at"]),
                "on_screen_action": shot["on_screen_action"],
                "actual_action_interval": shot["actual_action_interval"],
                "camera_focus": {**shot["camera"], "subject": shot["expected_visible_state"]},
                "expected_visible_state": shot["expected_visible_state"],
                "proof": shot["proof"],
                "source_sha256": shot["source_sha256"],
                "image_review": "SEE_REVIEW_R2_AND_FINAL_FRAMES",
            }
            for shot in actual_shots
        ],
        "captions": cues,
        "movies": [
            {
                "file": v.name,
                "sha256": sha(v),
                "bytes": v.stat().st_size,
                "full_decode_exit_code": 0,
            }
            for v in (movie, burned)
        ],
    }
    (out / "edit_project.json").write_text(
        json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps({"status": final["status"], "duration": offset, "movies": final["movies"]}),
        flush=True,
    )


if __name__ == "__main__":
    main()
