"""Reálné záznamy VS Code, browseru, Codegenu a Trace Vieweru se souvislým komentářem."""

import argparse
import hashlib
import json
import os
import shutil
import site
import subprocess
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

site.addsitedir(str(Path(__file__).resolve().parents[2] / ".tools/media-env/Lib/site-packages"))

from continuous_speech import LEXICON, prepare  # noqa: E402
from studio import (  # noqa: E402
    OUTPUT,
    PYTHON,
    ROOT,
    WORKSPACE,
    Studio,
    focus,
    gui,
    owns_foreground,
    paste,
    record_window,
    recording_surface,
)

STOP_REQUEST = ROOT / "evidence/stop-recording.request"


class RecordingStopped(Exception):
    pass


def capture_events(process, log, handle, events, duration, require_foreground=True):
    started = time.monotonic()
    next_event = 0
    try:
        while process.poll() is None:
            if STOP_REQUEST.exists():
                raise RecordingStopped("Natáčení zastavené vlastníkem.")
            if require_foreground and not owns_foreground(handle):
                raise RuntimeError("Cizí okno převzalo popředí; dílčí záznam se nepřijímá.")
            elapsed = time.monotonic() - started
            while next_event < len(events) and elapsed >= events[next_event][0]:
                focus(handle)
                events[next_event][1]()
                next_event += 1
                elapsed = time.monotonic() - started
            if elapsed > duration + 30:
                raise RuntimeError("Záznam překročil skutečnou délku audia.")
            time.sleep(0.15)
    finally:
        # Při chybě UI nebo přerušení nesmí capture pokračovat po zavření
        # vlastní aplikace a zachytit jiná okna pracovní plochy.
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        log.close()


def read_json(path):
    for _ in range(10):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            time.sleep(0.1)
    raise ValueError(f"Neúplný JSON: {path.name}")


def media_info(path):
    import re

    from studio import ffmpeg

    result = subprocess.run(
        [ffmpeg(), "-hide_banner", "-i", str(path)],
        capture_output=True,
        text=True,
        errors="replace",
    )
    match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", result.stderr)
    if not match:
        raise ValueError(f"Nelze ověřit skutečnou délku {path.name}.")
    hours, minutes, seconds = map(float, match.groups())
    return {"duration": hours * 3600 + minutes * 60 + seconds, "probe": result.stderr}


def current_audio(scene, timeout=1200):
    spoken, _ = prepare(scene["paragraph"], read_json(LEXICON))
    directory = ROOT / "video_course/narration/vlasta"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for sidecar in directory.glob(f"{scene['id']}_*.json"):
            data = read_json(sidecar)
            if data.get("spoken_text") == spoken and data.get("display_text") == scene["paragraph"]:
                audio = ROOT / data["audio"]
                if (
                    audio.is_file()
                    and hashlib.sha256(audio.read_bytes()).hexdigest() == data["audio_sha256"]
                ):
                    return data
        time.sleep(2)
    raise TimeoutError(f"Není připravené aktuální audio scény {scene['id']}.")


def ensure_sources():
    assert str(WORKSPACE) == "C:\\QA\\PlaywrightAcademy"
    if not PYTHON.exists():
        raise RuntimeError("Chybí ověřená natáčecí instalace.")
    for name in (
        "demo_app",
        "tests",
        "training",
        "test_data",
        "pages",
        "tests_external",
        "scripts",
        "docs",
    ):
        shutil.copytree(
            ROOT / name,
            WORKSPACE / name,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for name in ("README.md", "pyproject.toml", "requirements.lock", "conftest.py", ".env.example"):
        shutil.copyfile(ROOT / name, WORKSPACE / name)


def ensure_demo():
    from demo_app.app import source_fingerprint

    expected_build = source_fingerprint()

    def healthy():
        try:
            with urllib.request.urlopen("http://127.0.0.1:5000/health", timeout=2) as response:
                data = json.loads(response.read())
                if (
                    data.get("service") == "playwright-academy"
                    and data.get("build_id") != expected_build
                ):
                    raise RuntimeError(
                        "Na portu5000 běží jiná verze dema; nezastavuji cizí proces."
                    )
                return (
                    data.get("service") == "playwright-academy"
                    and data.get("build_id") == expected_build
                )
        except OSError:
            return False

    if healthy():
        return None
    log = (OUTPUT / "demo-process.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        [str(PYTHON), "-m", "demo_app.app"],
        cwd=WORKSPACE,
        env={**os.environ, "PYTHONUTF8": "1"},
        stdout=log,
        stderr=log,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if healthy():
            return process
        if process.poll() is not None:
            raise RuntimeError("Demo se nespustilo. Zkontrolujte demo-process.log.")
        time.sleep(0.3)
    raise TimeoutError("Lokální demo není připravené.")


def write_first_events(studio):
    path = Path("tests/examples/test_video_created.py")
    final_text = (ROOT / path).read_text(encoding="utf-8")
    (WORKSPACE / path).write_text("", encoding="utf-8")
    handle = studio.editor_file(str(path))
    lines = final_text.splitlines(keepends=True)
    cuts = [min(len(lines), n) for n in (4, 7, 8, 9, len(lines))]

    def edit(count):
        focus(handle)
        gui.hotkey("ctrl", "a")
        paste("".join(lines[:count]))
        gui.hotkey("ctrl", "s")

    return handle, [(4 + i * 8, lambda cut=cut: edit(cut)) for i, cut in enumerate(cuts)]


def prepare_scene(studio, scene, audio_data):
    screen = dict(scene["screen"])
    scene["effective_screen"] = screen
    kind, action = screen["kind"], screen.get("action")
    if kind == "editor":
        if action == "select_interpreter":
            return studio.interpreter_selection()
        if scene["chapter"] == 8 and screen.get("source") == "tests/regression/test_records.py":
            text = (WORKSPACE / screen["source"]).read_text(encoding="utf-8").splitlines()
            screen["line"] = next(i for i, line in enumerate(text, 1) if "def test_12_" in line)
        if action == "write_first":
            return write_first_events(studio)
        if screen.get("source", "").endswith("codegen_draft.py"):
            # Skutečný export uzavřením nahrávacího browseru; žádné vytvoření falešného draftu.
            if studio.codegen_process and studio.codegen_process.poll() is None:
                import win32con
                import win32gui

                win32gui.PostMessage(studio.codegen_window, win32con.WM_CLOSE, 0, 0)
                studio.codegen_process.wait(timeout=20)
            draft = WORKSPACE / screen["source"]
            if not draft.exists() or "def test_" not in draft.read_text(encoding="utf-8"):
                raise RuntimeError("Codegen nevytvořil skutečný pytest draft.")
            destination = ROOT / "evidence/codegen"
            destination.mkdir(exist_ok=True)
            shutil.copyfile(draft, destination / "original_codegen_draft.py")
        events = []
        if scene["id"] == "07_00":
            cursor = 0
            needle = scene["paragraph"].find("Na obrazovce jsou tři")
            for cue in audio_data["cues"]:
                left = scene["paragraph"].find(cue["text"], cursor)
                cursor = left + len(cue["text"])
                if left <= needle < cursor:
                    events.append(
                        (
                            cue["start"],
                            lambda: studio.editor_file(
                                "training/solutions/test_07_parametrize.py", 1
                            ),
                        )
                    )
                    break
        return studio.editor_file(screen["source"], screen.get("line", 1)), events
    if kind == "terminal":
        scene["terminal_prepared_at"] = time.time()
        handle, callback = studio.terminal(action, scene["id"])
        return handle, [(1, callback)]
    if kind == "browser":
        focus(studio.browser_window)
        if scene["id"] in {"06_00", "08_00"}:
            from browser_story import prepare_story

            return prepare_story(studio, scene, audio_data)
        return studio.browser_window, [(1, lambda: studio.browser_action(action))]
    if kind == "codegen":
        handle, callback = studio.codegen(action == "inspect")
        return handle, [(2, callback)]
    if kind == "trace":
        handle, callback = studio.trace()
        return handle, [(2, callback)]
    if kind == "inspector":
        handle, callback = studio.debug()
        return handle, [(2, callback)]
    raise ValueError(f"Neznámý typ scény: {kind}")


def terminal_junit(scene):
    action = scene["screen"].get("action")
    if action in {"versions", "setup"}:
        return None
    filename = {"failure": "failure.xml", "fixed": "fixed.xml"}.get(action, "junit.xml")
    path = WORKSPACE / "reports" / filename
    if not path.exists() or path.stat().st_mtime < scene["terminal_prepared_at"]:
        raise RuntimeError(f"Chybí čerstvý JUnit skutečného příkazu: {scene['id']}")
    root = ET.parse(path).getroot()
    cases = root.findall(".//testcase")
    failures, errors = root.findall(".//failure"), root.findall(".//error")
    if not cases or errors:
        raise RuntimeError(f"JUnit obsahuje chybu přípravy/úklidu nebo žádné testy: {scene['id']}")
    artifacts = []
    if action == "failure":
        if (
            len(cases) != 1
            or len(failures) != 1
            or not cases[0].get("name", "").startswith("test_wrong_heading[")
        ):
            raise RuntimeError("Řízené selhání není očekávaný assertion test_wrong_heading.")
        if "AssertionError" not in (failures[0].get("message", "") + (failures[0].text or "")):
            raise RuntimeError("Výuková chyba není očekávaný assertion.")
        for name in ("playwright_screenshot", "playwright_trace", "playwright_video"):
            item = cases[0].find(f"./properties/property[@name='{name}']")
            if item is None and name == "playwright_video":
                continue
            artifact = WORKSPACE / item.get("value") if item is not None else None
            if (
                artifact is None
                or not artifact.exists()
                or artifact.stat().st_mtime < scene["terminal_prepared_at"]
            ):
                raise RuntimeError(f"Chybí čerstvý důkaz řízené chyby: {name}")
            archive = (
                ROOT / "evidence/recorded-artifacts" / scene["id"] / artifact.relative_to(WORKSPACE)
            )
            archive.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(artifact, archive)
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            if hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
                raise RuntimeError("Archivovaný důkaz se liší od skutečného artefaktu.")
            artifacts.append(
                {
                    "path": str(artifact.relative_to(WORKSPACE)),
                    "archive": str(archive.relative_to(ROOT)),
                    "sha256": digest,
                }
            )
    elif failures:
        raise RuntimeError(f"Úspěšný příkaz má selhání v JUnit: {scene['id']}")
    # Hostname je osobní označení stanice. Výsledky případů zachováváme;
    # před zobrazením XML odstraníme pouze tento atribut a úpravu přiznáme.
    for suite in root.iter("testsuite"):
        suite.attrib.pop("hostname", None)
    tree = ET.ElementTree(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    evidence = ROOT / "evidence/recorded-commands"
    evidence.mkdir(exist_ok=True)
    copy = evidence / f"{scene['id']}.xml"
    shutil.copyfile(path, copy)
    archived_reports = []
    if action in {"failure", "fixed"}:
        for report in (path, path.with_suffix(".html")):
            archive = (
                ROOT / "evidence/recorded-artifacts" / scene["id"] / report.relative_to(WORKSPACE)
            )
            archive.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(report, archive)
            archived_reports.append(
                {
                    "archive": str(archive.relative_to(ROOT)),
                    "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                }
            )
    return {
        "testcases": len(cases),
        "failures": len(failures),
        "errors": len(errors),
        "junit": str(copy.relative_to(ROOT)),
        "sha256": hashlib.sha256(copy.read_bytes()).hexdigest(),
        "artifacts": artifacts,
        "archived_reports": archived_reports,
        "redactions": ["testsuite hostname removed"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="01_00")
    parser.add_argument("--stop")
    parser.add_argument("--scenes", nargs="+", help="Přetočit jen vybrané scény.")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    STOP_REQUEST.unlink(missing_ok=True)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    ensure_sources()
    demo = ensure_demo()
    subprocess.run(
        [
            str(ROOT / ".venv/Scripts/python.exe"),
            str(ROOT / "video_course/production/open_studio.py"),
            "--workspace",
            str(WORKSPACE),
            *(
                ["--enable-python"]
                if any(
                    item["screen"].get("action") == "select_interpreter"
                    for item in read_json(ROOT / "video_course/storyboard/course_plan.json")
                    if args.start <= item["id"]
                    and (not args.stop or item["id"] <= args.stop)
                    and (not args.scenes or item["id"] in args.scenes)
                )
                else []
            ),
        ],
        check=True,
    )
    try:
        studio = Studio()
    except Exception:
        if demo is not None and demo.poll() is None:
            demo.terminate()
        raise
    plan_path = ROOT / "video_course/storyboard/course_plan.json"
    plan = read_json(plan_path)
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from freeze_reference import current

    reference_hash = hashlib.sha256(json.dumps(current(), sort_keys=True).encode()).hexdigest()
    entries = [
        p
        for p in plan
        if p["id"] >= args.start
        and (not args.stop or p["id"] <= args.stop)
        and (not args.scenes or p["id"] in args.scenes)
    ]
    if args.scenes and set(args.scenes) - {p["id"] for p in plan}:
        raise ValueError("Neznámé scény k natáčení.")
    # Živý Codegen má stav nahraných akcí. Po restartu jej nelze obnovit
    # přeskočením jeho úvodu a otevřením nového prázdného Inspectoru.
    codegen_group = {"09_00", "09_01", "09_02"}
    replay_codegen = any(p["id"] in codegen_group for p in entries)
    if replay_codegen:
        chosen = {p["id"] for p in entries} | codegen_group
        entries = [p for p in plan if p["id"] in chosen]
    try:
        for number, scene in enumerate(entries, 1):
            # Výklad se může po nezávislé obsahové kontrole zpřesnit ještě
            # před natočením pozdější kapitoly. Načteme aktuální deklaraci.
            scene = next(item for item in read_json(plan_path) if item["id"] == scene["id"])
            data = current_audio(scene)
            audio = ROOT / data["audio"]
            duration = media_info(audio)["duration"]
            target = OUTPUT / f"{scene['id']}.mp4"
            receipt = target.with_suffix(".json")
            identity = hashlib.sha256(
                json.dumps(
                    {
                        "audio": data["signature"],
                        "screen": scene["screen"],
                        "source_reference": reference_hash,
                    },
                    sort_keys=True,
                ).encode()
            ).hexdigest()
            if (
                args.resume
                and target.exists()
                and receipt.exists()
                and not (replay_codegen and scene["id"] in codegen_group)
            ):
                prior = read_json(receipt)
                if (
                    prior.get("identity") == identity
                    and prior.get("status") == "recorded"
                    and prior.get("clip_sha256") == hashlib.sha256(target.read_bytes()).hexdigest()
                ):
                    print(
                        json.dumps({"scene": scene["id"], "status": "retained_verified_recording"}),
                        flush=True,
                    )
                    continue
            in_progress = receipt.with_suffix(".recording.tmp")
            in_progress.write_text(
                json.dumps(
                    {"scene": scene["id"], "identity": identity, "status": "recording_in_progress"}
                ),
                encoding="utf-8",
            )
            in_progress.replace(receipt)
            handle, events = prepare_scene(studio, scene, data)
            # Jediný záměrný přechod do jiného okna: skutečný headed test
            # otevře vlastní Chromium nad terminálem a po dokončení ho zavře.
            protected = not (
                scene["screen"]["kind"] == "terminal" and scene["screen"].get("action") == "journey"
            )
            with recording_surface(handle, enabled=protected):
                process, log = record_window(handle, audio, target, duration)
                capture_events(process, log, handle, events, duration, protected)
            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg selhal ve scéně {scene['id']}; viz její log.")
            actual = media_info(target)
            if abs(actual["duration"] - duration) > 1:
                raise RuntimeError(f"Nesouhlasí délka obrazu a komentáře ve scéně {scene['id']}.")
            from PIL import Image, ImageStat
            from studio import ffmpeg

            frames = ROOT / "evidence/video-frames" / scene["id"]
            frames.mkdir(parents=True, exist_ok=True)
            for index, fraction in enumerate((0.1, 0.5, 0.9)):
                frame = frames / f"{index}.png"
                subprocess.run(
                    [
                        ffmpeg(),
                        "-y",
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-ss",
                        str(actual["duration"] * fraction),
                        "-i",
                        str(target),
                        "-frames:v",
                        "1",
                        str(frame),
                    ],
                    check=True,
                )
                with Image.open(frame) as snapshot:
                    stats = ImageStat.Stat(snapshot.convert("L"))
                if stats.stddev[0] < 3:
                    raise RuntimeError(f"Prázdný nebo černý obraz ve scéně {scene['id']}.")
            terminal_evidence = None
            junit_evidence = None
            if scene["screen"]["kind"] == "terminal":
                terminal_evidence = read_json(
                    WORKSPACE / "reports" / f"terminal_{scene['id']}.json"
                )
                expected_exit = 1 if scene["screen"].get("action") == "failure" else 0
                if terminal_evidence.get("exit_code") != expected_exit:
                    raise RuntimeError(
                        f"Terminál nemá očekávaný skutečný exit code ve scéně {scene['id']}."
                    )
                junit_evidence = terminal_junit(scene)
            result = {
                "scene": scene["id"],
                "identity": identity,
                "status": "recorded",
                "source_screen": scene["screen"],
                "effective_screen": scene.get("effective_screen", scene["screen"]),
                "narration_action_cues": scene.get("narration_action_cues", []),
                "audio": data["audio"],
                "duration": actual["duration"],
                "cues": data["cues"],
                "source_reference": reference_hash,
                "terminal_result": terminal_evidence,
                "junit_result": junit_evidence,
                "voice": data["voice"],
                "screen_recording": "real_gdigrab_visible_desktop_cropped_to_own_window",
                "foreground_protection": (
                    "temporary_topmost_and_foreground_checks"
                    if protected
                    else "unlocked_for_actual_headed_test_window; visual_review_required"
                ),
                "visual_review": "pending",
                "human_listening_review": "not_claimed",
            }
            receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            status = {
                "completed": number,
                "selected": len(entries),
                "scene": scene["id"],
                "chapter": scene["chapter"],
                "duration": actual["duration"],
                "status": "recorded",
            }
            (ROOT / "evidence/recording-progress.json").write_text(
                json.dumps(status), encoding="utf-8"
            )
            print(json.dumps(status), flush=True)
    except RecordingStopped:
        print(
            json.dumps({"status": "stopped_by_owner", "partial_scene_accepted": False}), flush=True
        )
    finally:
        studio.close()
        if demo is not None and demo.poll() is None:
            demo.terminate()


if __name__ == "__main__":
    main()
