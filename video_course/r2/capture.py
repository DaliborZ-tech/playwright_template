"""Real VS Code/browser/terminal shots for the single R2 reference chapter."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "video_course/production"))
from record_course import ensure_demo, ensure_sources, media_info  # noqa: E402
from studio import (  # noqa: E402
    WORKSPACE,
    Studio,
    ffmpeg,
    focus,
    gui,
    owns_foreground,
    paste,
    recording_surface,
    win32gui,
)

SOURCE = "tests/examples/test_video_created.py"
NODE = SOURCE + "::test_video_login_form"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Lesson:
    def __init__(self, run_group="capture"):
        (ROOT / "video_course/recordings").mkdir(parents=True, exist_ok=True)
        ensure_sources()
        self.demo = ensure_demo()
        subprocess.run(
            [
                str(ROOT / ".venv/Scripts/python.exe"),
                str(ROOT / "video_course/production/open_studio.py"),
                "--workspace",
                str(WORKSPACE),
                "--r2",
            ],
            check=True,
        )
        self.studio = Studio(editor_title="Playwright Academy Studio R2")
        self.buffer = ""
        self.terminals = {}
        self.runs = {}
        self.run_group = run_group
        self.dom_open = False
        self.cdp = self.studio.context.new_cdp_session(self.studio.page)
        self.inspect_events = []
        self.cdp.on("Overlay.inspectNodeRequested", lambda e: self.inspect_events.append(e))

    def source(self):
        return WORKSPACE / SOURCE

    def append(self, text):
        gui.hotkey("ctrl", "end")
        # Actual editing in the visible editor. Paste short tokens to avoid
        # keyboard-layout substitution of punctuation on Czech Windows.
        for part in text.splitlines(keepends=True):
            for token in part.rstrip("\n").split(" "):
                if token:
                    paste(token)
                gui.write(" ")
                time.sleep(0.10)
            gui.press("backspace")
            if part.endswith("\n"):
                gui.press("enter")
        self.buffer += text
        gui.hotkey("ctrl", "s")
        time.sleep(0.3)
        actual = self.source().read_text(encoding="utf-8")
        if actual != self.buffer:
            raise RuntimeError(f"Actual editor content differs: {actual!r} vs {self.buffer!r}")
        gui.press("home")
        gui.keyDown("shift")
        gui.press("up")
        gui.press("home")
        gui.keyUp("shift")
        return {"file": SOURCE, "sha256": sha(self.source()), "text": actual}

    def replace_expected(self, before, after):
        self.studio.editor_file(SOURCE)
        expected = self.buffer.replace(before, after)
        gui.hotkey("ctrl", "g")
        line_number = next(
            i for i, line in enumerate(self.buffer.splitlines(), 1) if before in line
        )
        paste(str(line_number))
        gui.press("enter")
        time.sleep(0.5)
        gui.hotkey("ctrl", "l")
        time.sleep(0.2)
        gui.hotkey("ctrl", "c")
        time.sleep(0.2)
        import pyperclip

        selected = pyperclip.paste().replace("\r\n", "\n")
        if selected.rstrip("\n") != self.buffer.splitlines()[line_number - 1]:
            raise RuntimeError(f"Actual selected editor line differs: {selected!r}")
        time.sleep(0.4)
        paste(expected.splitlines()[line_number - 1] + "\n")
        gui.hotkey("ctrl", "s")
        time.sleep(0.3)
        if self.source().read_text(encoding="utf-8") != expected:
            raise RuntimeError("Expected-text edit was not performed in actual editor")
        self.buffer = expected
        return {
            "file": SOURCE,
            "before": before,
            "after": after,
            "sha256": sha(self.source()),
            "text": expected,
        }

    def inspect(self, role, name):
        page = self.studio.page
        if self.dom_open:
            focus(self.studio.browser_window)
            gui.press("f12")
            time.sleep(0.5)
            self.dom_open = False
        page.goto("http://127.0.0.1:5000/login")
        focus(self.studio.browser_window)
        gui.press("f12")
        time.sleep(1.2)
        self.dom_open = True
        self.cdp.send("DOM.enable")
        self.cdp.send("Overlay.enable")
        gui.hotkey("ctrl", "shift", "c")
        time.sleep(0.3)
        target = page.get_by_role(role, name=name, exact=(role == "heading"))
        box = target.bounding_box()
        geometry = page.evaluate("({y:screenY+outerHeight-innerHeight,dpr:devicePixelRatio})")
        left = max(0, win32gui.GetWindowRect(self.studio.browser_window)[0])
        self.inspect_events.clear()
        gui.click(
            round(left + (box["x"] + box["width"] / 2) * geometry["dpr"]),
            round((geometry["y"] + box["y"] + box["height"] / 2 - 7) * geometry["dpr"]),
        )
        page.wait_for_timeout(500)
        from pywinauto import Desktop

        own = Desktop(backend="uia").window(handle=self.studio.browser_window)
        nodes = own.descendants(control_type="TreeItem")
        selected = []
        for node in nodes:
            try:
                active = node.is_selected()
            except Exception:
                try:
                    active = bool(node.legacy_properties().get("State", 0) & 2)
                except Exception:
                    active = False
            if active:
                selected.append(node.window_text())
        wanted = "h2" if role == "heading" else "button"
        if not any(wanted in item and name in item for item in selected):
            gui.screenshot().save(str(HERE / "dom-selection-failed.png"))
            (HERE / "dom-uia.json").write_text(
                json.dumps(
                    {"selected": selected, "nodes": [n.window_text() for n in nodes]},
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            raise RuntimeError(f"Actual selected DevTools row does not prove {wanted}: {selected}")
        html = target.evaluate("element => element.outerHTML")
        if name not in html:
            raise RuntimeError(f"Wrong selected DOM node: {html}")
        return {
            "role": role,
            "name": name,
            "actual_dom": html,
            "node_name": wanted.upper(),
            "selected_devtools_rows": selected,
            "selection": (
                "Actual DevTools element picker, selected accessible DOM row and real outerHTML"
            ),
        }

    def prepare(self, shot):
        action = shot["on_screen_action"]
        if shot["view"] == "test_video":
            return None
        if shot["view"] == "editor":
            handle = self.studio.editor_file(SOURCE)
            if action == "blank":
                gui.hotkey("ctrl", "a")
                gui.press("backspace")
                gui.hotkey("ctrl", "s")
                self.buffer = ""
            return handle
        if shot["view"] == "terminal":
            color = "red" if action.startswith("red") else "green"
            if action.endswith("command"):
                folder = f"reports/r2/{self.run_group}/{color}"
                self.studio.commands[action] = (
                    f".\\.venv\\Scripts\\python.exe -m pytest {NODE} "
                    "-q --headed --slowmo=400 "
                    f"--video=on --tracing=off --output={folder}/artifacts "
                    f"--html={folder}/report.html "
                    f"--junitxml={folder}/junit.xml"
                )
                h, _ = self.studio.terminal(action, "r2_" + color)
                self.terminals[color] = h
                return h
            focus(self.studio.editor)
            # Editor_file closed the panel while showing the fix.
            from pywinauto import Desktop

            own = Desktop(backend="uia").window(handle=self.studio.editor)
            terminal_tabs = [
                tab
                for tab in own.descendants(control_type="TabItem")
                if tab.window_text().startswith("Terminal")
            ]
            if not terminal_tabs:
                gui.hotkey("ctrl", "j")
            time.sleep(0.3)
            maximize = own.child_window(title="Maximize Panel", control_type="Button")
            if maximize.exists(timeout=0.5):
                maximize.click_input()
            gui.click(700, 220)
            return self.studio.editor
        focus(self.studio.browser_window)
        return self.studio.browser_window

    def run(self, color):
        status = WORKSPACE / f"reports/terminal_r2_{color}.json"
        started = time.time()
        gui.press("enter")
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if status.exists() and status.stat().st_mtime > started:
                data = read(status)
                if data["exit_code"] != 777:
                    break
            time.sleep(0.2)
        else:
            raise RuntimeError("Actual pytest command did not complete")
        expected = 1 if color == "red" else 0
        if data["exit_code"] != expected:
            raise RuntimeError(f"Unexpected actual pytest exit: {data}")
        folder = WORKSPACE / f"reports/r2/{self.run_group}/{color}"
        tree = ET.parse(folder / "junit.xml")
        cases = tree.findall(".//testcase")
        failures, errors = tree.findall(".//failure"), tree.findall(".//error")
        if len(cases) != 1 or len(failures) != expected or errors or tree.findall(".//skipped"):
            raise RuntimeError("Actual JUnit does not prove the intended RED/GREEN case")
        case_name = cases[0].attrib["name"]
        class_name = cases[0].attrib["classname"]
        actual_nodeid = class_name.replace(".", "/") + ".py::" + case_name
        if actual_nodeid.split("[")[0] != NODE:
            raise RuntimeError(f"Actual JUnit is a different test: {actual_nodeid}")
        if (folder / "junit.xml").stat().st_mtime < started:
            raise RuntimeError("JUnit predates this run")
        if color == "red" and "Neexistující nadpis" not in failures[0].text:
            raise RuntimeError("Failure is not the intended assertion")
        for suite in tree.iter("testsuite"):
            suite.attrib.pop("hostname", None)
        tree.write(folder / "junit.xml", encoding="utf-8", xml_declaration=True)
        target = HERE / "evidence" / self.run_group / color
        if target.exists():
            raise RuntimeError("Run evidence already exists; use a new take")
        shutil.copytree(folder, target)
        video = next(target.rglob("*.webm"))
        result = {
            "exit_code": expected,
            "testcases": 1,
            "failures": len(failures),
            "errors": 0,
            "nodeid": NODE,
            "actual_junit_nodeid": actual_nodeid,
            "classname": cases[0].attrib["classname"],
            "name": cases[0].attrib["name"],
            "source_sha256": sha(self.source()),
            "junit": str((target / "junit.xml").relative_to(ROOT)),
            "junit_sha256": sha(target / "junit.xml"),
            "browser_video": str(video.relative_to(ROOT)),
            "browser_video_sha256": sha(video),
            "report": str((target / "report.html").relative_to(ROOT)),
            "report_sha256": sha(target / "report.html"),
            "capture_unix_time": started,
        }
        self.runs[color] = result
        focus(self.studio.editor)
        return result

    def act(self, action):
        page = self.studio.page
        if action == "blank":
            return {
                "file": SOURCE,
                "actual_bytes": self.source().stat().st_size,
                "sha256": sha(self.source()),
            }
        if action == "type_import":
            return self.append(
                '"""Výsledek souboru vytvořeného od prázdné stránky během videokurzu."""\n\n'
                "from playwright.sync_api import Page, expect\n"
            )
        if action == "type_function":
            return self.append("\n\ndef test_video_login_form(page: Page) -> None:\n")
        if action == "type_goto":
            return self.append('    page.goto("/login")\n')
        if action == "save":
            gui.hotkey("ctrl", "s")
            return {"sha256": sha(self.source()), "file": SOURCE}
        if action == "type_heading":
            return self.append(
                '    expect(page.get_by_role("heading", name="Přihlášení", exact=True))'
                ".to_be_visible()\n"
            )
        if action == "type_button":
            return self.append(
                '    expect(page.get_by_role("button", name="Přihlásit se")).to_be_visible()\n'
            )
        if action == "make_red":
            return self.replace_expected('name="Přihlášení"', 'name="Neexistující nadpis"')
        if action == "make_green":
            return self.replace_expected('name="Neexistující nadpis"', 'name="Přihlášení"')
        if action == "final_code":
            expected = (ROOT / SOURCE).read_text(encoding="utf-8")
            assert self.source().read_text(encoding="utf-8") == expected
            gui.hotkey("ctrl", "home")
            return {"file": SOURCE, "matches_frozen_reference": True, "sha256": sha(self.source())}
        if action in {"red_command", "green_command"}:
            return {"command": self.studio.commands[action], "nodeid": NODE}
        if action in {"red_run", "green_run"}:
            return self.run(action.split("_")[0])
        if action == "red_detail":
            gui.hotkey("ctrl", "f")
            paste("Neexistující nadpis")
            gui.press("escape")
            return self.runs["red"]
        if action in {"red_result", "green_result"}:
            gui.hotkey("ctrl", "end")
            return self.runs[action.split("_")[0]]
        if action in {"inspect_heading", "inspect_button"}:
            return self.inspect(
                "heading" if action.endswith("heading") else "button",
                "Přihlášení" if action.endswith("heading") else "Přihlásit se",
            )
        if action == "open_report":
            if self.dom_open:
                gui.press("f12")
                self.dom_open = False
            page.goto((WORKSPACE / f"reports/r2/{self.run_group}/green/report.html").as_uri())
            page.get_by_text("1 Passed", exact=False).first.wait_for()
            return {
                "report_sha256": self.runs["green"]["report_sha256"],
                "title": page.title(),
                "actual_text": page.locator("body").inner_text(),
            }
        if action == "report_details":
            page.get_by_text("Show all details", exact=False).first.click()
            return {
                "actual_text": page.locator("body").inner_text(),
                "expected_case": "test_video_login_form",
            }
        if self.dom_open:
            gui.press("f12")
            self.dom_open = False
        if action in {"open_login", "exercise"}:
            page.goto("http://127.0.0.1:5000/login")
            if action == "exercise":
                page.get_by_label("E-mail", exact=True).fill("tester@example.test")
            return {
                "url": page.url,
                "heading": page.get_by_role("heading").all_text_contents(),
                "email_label": "E-mail",
            }
        if action == "fill_email":
            page.get_by_label("E-mail", exact=True).fill("tester@example.test")
            return {"actual_value": page.get_by_label("E-mail", exact=True).input_value()}
        if action == "fill_clear":
            page.get_by_label("Heslo", exact=True).fill("Academy123!")
            page.wait_for_timeout(1200)
            page.get_by_label("E-mail", exact=True).clear()
            page.get_by_label("Heslo", exact=True).clear()
            return {
                "email_empty": page.get_by_label("E-mail", exact=True).input_value() == "",
                "password_empty": page.get_by_label("Heslo", exact=True).input_value() == "",
            }
        raise ValueError(action)

    def close(self):
        self.studio.close()
        if self.demo is not None and self.demo.poll() is None:
            self.demo.terminate()


def record_shot(lesson, shot):
    folder = HERE / "recordings"
    folder.mkdir(exist_ok=True)
    target = folder / f"{shot['id']}.mp4"
    proof = {
        **shot,
        "status": "recording",
        "human_review": "pending",
        "run_group": lesson.run_group,
        "contract_sha256": sha(HERE / "capture_contract.json"),
    }
    if shot["view"] == "test_video":
        color = shot["on_screen_action"].split("_")[0]
        source = ROOT / lesson.runs[color]["browser_video"]
        # Real pytest browser footage, explicitly labelled; never a fabricated UI.
        subprocess.run(
            [
                ffmpeg(),
                "-y",
                "-v",
                "error",
                "-i",
                str(source),
                "-vf",
                "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,tpad=stop_mode=clone:stop_duration=10",
                "-t",
                str(shot["duration"]),
                "-r",
                "25",
                "-c:v",
                "libx264",
                "-threads",
                "4",
                "-crf",
                "18",
                "-an",
                str(target),
            ],
            check=True,
        )
        proof.update(
            proof=lesson.runs[color],
            capture_method="actual_pytest_browser_recording",
            action_started=0,
            action_finished=min(media_info(source)["duration"], shot["duration"]),
            held_after_browser_closed=True,
        )
    else:
        handle = lesson.prepare(shot)
        action = shot["on_screen_action"]
        log = target.with_suffix(".log").open("w", encoding="utf-8")
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
            "-threads",
            "4",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(target),
        ]
        with recording_surface(handle):
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=log, stderr=log)
            started = time.monotonic()
            try:
                time.sleep(max(0.4, shot["action_offset"]))
                proof["action_started"] = time.monotonic() - started
                proof["proof"] = lesson.act(action)
                proof["action_finished"] = time.monotonic() - started
                while time.monotonic() - started < shot["duration"]:
                    if (ROOT / "evidence/stop-recording.request").exists():
                        raise RuntimeError("Recording stopped by owner")
                    if not owns_foreground(handle) and action not in {"red_run", "green_run"}:
                        raise RuntimeError("Foreign foreground; partial shot rejected")
                    time.sleep(0.1)
                process.communicate(input=b"q\n", timeout=15)
            finally:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                log.close()
        if process.returncode:
            raise RuntimeError(f"Actual capture failed: {shot['id']}")
        proof["capture_method"] = "real_own_application_desktop_capture"
    info = media_info(target)
    proof.update(
        status="captured",
        actual_duration=info["duration"],
        clip=str(target.relative_to(ROOT)),
        clip_sha256=sha(target),
    )
    for index, at in enumerate(
        (0.3, min(info["duration"] - 0.1, proof["action_finished"] + 0.4), info["duration"] - 0.3)
    ):
        out = HERE / "evidence/frames" / f"{shot['id']}_{index}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                ffmpeg(),
                "-y",
                "-v",
                "error",
                "-ss",
                str(max(0, at)),
                "-i",
                str(target),
                "-frames:v",
                "1",
                str(out),
            ],
            check=True,
        )
    target.with_suffix(".json").write_text(
        json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {"shot": shot["id"], "seconds": info["duration"], "action": shot["on_screen_action"]}
        ),
        flush=True,
    )
    return proof


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-dom", action="store_true")
    parser.add_argument("--rehearsal", action="store_true")
    args = parser.parse_args()
    (ROOT / "evidence/stop-recording.request").unlink(missing_ok=True)
    lesson = Lesson(("rehearsal_" if args.rehearsal else "take_") + str(int(time.time())))
    try:
        if args.preflight_dom:
            result = lesson.inspect("heading", "Přihlášení")
            (HERE / "dom-preflight.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            gui.screenshot().save(str(HERE / "dom-preflight.png"))
            print(result)
            return
        timeline = read(HERE / "timeline.json")
        if not args.rehearsal:
            inputs = [HERE / name for name in ("plan.json", "timeline.json", "narration.wav")]
            for section in timeline["sections"]:
                audio = ROOT / section["audio"]
                inputs.extend((audio, audio.with_suffix(".json")))
            contract = {
                "run_group": lesson.run_group,
                "voice": "cs-CZ-VlastaNeural",
                "inputs_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs},
            }
            (HERE / "capture_contract.json").write_text(
                json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        receipts = []
        for shot in timeline["shots"]:
            if args.rehearsal:
                if shot["view"] == "test_video":
                    continue
                handle = lesson.prepare(shot)
                with recording_surface(handle):
                    result = lesson.act(shot["on_screen_action"])
                receipts.append({"shot": shot["id"], "proof": result})
                print(json.dumps({"rehearsal": shot["id"], "status": "verified"}), flush=True)
            else:
                receipts.append(record_shot(lesson, shot))
        if args.rehearsal:
            (HERE / "rehearsal.json").write_text(
                json.dumps(receipts, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            return
        (HERE / "capture.json").write_text(
            json.dumps(receipts, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if lesson.runs["red"]["nodeid"] != lesson.runs["green"]["nodeid"]:
            raise RuntimeError("RED and GREEN are not the same case")
    finally:
        lesson.close()


if __name__ == "__main__":
    main()
