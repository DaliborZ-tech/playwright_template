"""Record actual CLI Codegen browser, typing and Inspector; no simulated UI."""

import hashlib
import json
import subprocess
import sys
import time
from contextlib import ExitStack, contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "video_course/r2"))
import capture as recorder  # noqa: E402
from pywinauto import Desktop  # noqa: E402
from studio import (  # noqa: E402
    PYTHON,
    WORKSPACE,
    focus,
    gui,
    paste,
    tool_windows,
    win32gui,
)


@contextmanager
def tiled_surface(handle):
    # Unlike the generic fullscreen recorder, preserve the deliberate two-window layout.
    prior = win32gui.GetWindowLong(handle, -20)
    win32gui.SetWindowPos(handle, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
    gui.press("alt")
    win32gui.SetForegroundWindow(handle)
    gui.press("escape")
    try:
        yield
    finally:
        win32gui.SetWindowPos(handle, -1 if prior & 8 else -2, 0, 0, 0, 0, 0x0001 | 0x0002)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Codegen:
    def __init__(self):
        self.run_group = f"codegen_{int(time.time())}"
        recorder.ensure_sources()
        self.demo = recorder.ensure_demo()
        self.draft = WORKSPACE / "reports/r21-codegen/draft.py"
        self.draft.parent.mkdir(parents=True, exist_ok=True)
        self.draft.unlink(missing_ok=True)
        before_inspector = set(tool_windows("Playwright Inspector"))
        before_browser = set(tool_windows("Playwright Academy"))
        self.command = [
            str(PYTHON),
            "-m",
            "playwright",
            "codegen",
            "--target=python-pytest",
            "--viewport-size=1100,900",
            "--output=reports/r21-codegen/draft.py",
            "http://127.0.0.1:5000/login",
        ]
        self.log = (HERE / "codegen-process.log").open("w", encoding="utf-8")
        self.process = subprocess.Popen(
            self.command, cwd=WORKSPACE, stdout=self.log, stderr=self.log
        )
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            inspectors = set(tool_windows("Playwright Inspector")) - before_inspector
            browsers = set(tool_windows("Playwright Academy")) - before_browser
            if inspectors and browsers:
                self.inspector, self.browser = next(iter(inspectors)), next(iter(browsers))
                break
            time.sleep(0.3)
        else:
            raise RuntimeError("Owned newly launched Codegen windows did not appear")

    def prepare(self, shot):
        if shot["on_screen_action"] == "cg_inspector":
            focus(self.inspector)
            gui.press("escape")
            gui.hotkey("ctrl", "0")
            gui.keyDown("ctrl")
            gui.press("add", presses=3, interval=0.15)
            gui.keyUp("ctrl")
            gui.click(1200, 800)
            gui.press("escape")
            return self.inspector
        for handle, x, width in ((self.browser, 0, 1100), (self.inspector, 1100, 820)):
            win32gui.ShowWindow(handle, 9)
            win32gui.SetWindowPos(handle, -1, x, 0, width, 1032, 0x0040)
        gui.press("alt")
        win32gui.SetForegroundWindow(self.browser)
        time.sleep(0.5)
        return self.browser

    def act(self, action):
        if action == "cg_open":
            gui.moveTo(600, 690, duration=0.4)
        elif action == "cg_fill":
            window = Desktop(backend="uia").window(handle=self.browser)
            fields = window.descendants(control_type="Edit")
            field = next((f for f in fields if f.window_text() == "E-mail"), None)
            if field is None:
                # Actual native keyboard navigation, verified by Codegen's
                # emitted locator/value below, independent of UIA support.
                gui.click(600, 718)
            else:
                field.click_input()
            paste("tester@example.test")
            time.sleep(1)
        else:
            gui.moveTo(100, 100, duration=0.2)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            text = self.draft.read_text(encoding="utf-8") if self.draft.exists() else ""
            if "page.goto" in text and (action == "cg_open" or "tester@example.test" in text):
                break
            time.sleep(0.2)
        else:
            raise RuntimeError("CLI --output did not prove recorded action")
        if action != "cg_open" and 'get_by_role("textbox", name="E-mail").fill' not in text:
            raise RuntimeError("Codegen did not record the actual E-mail textbox")
        destination = HERE / "evidence/codegen" / (action + ".py")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
        return {
            "method": "Actual playwright codegen CLI, actual browser input, native Inspector",
            "cli": self.command[1:],
            "owned_process_pid": self.process.pid,
            "generated_source": str(destination.relative_to(ROOT)),
            "generated_sha256": sha(destination),
            "generated_text": text,
            "public_synthetic_account": True,
        }

    def close(self):
        for handle in (self.browser, self.inspector):
            if win32gui.IsWindow(handle):
                win32gui.PostMessage(handle, 0x0010, 0, 0)
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=5)
        self.log.close()
        if self.demo:
            self.demo.terminate()


def main():
    recorder.HERE = HERE
    recorder.recording_surface = tiled_surface
    audio = json.loads((HERE / "codegen_narration.json").read_text(encoding="utf-8"))
    contract = {"inputs_sha256": {audio["audio"]: sha(ROOT / audio["audio"])}}
    (HERE / "capture_contract.json").write_text(json.dumps(contract, indent=2), encoding="utf-8")
    lesson = Codegen()
    receipts = []
    try:
        with ExitStack() as stack:
            for handle in (lesson.browser, lesson.inspector):
                stack.enter_context(tiled_surface(handle))
            for action, duration in (("cg_open", 12), ("cg_fill", 12), ("cg_inspector", 24)):
                shot = {
                    "id": action,
                    "on_screen_action": action,
                    "duration": duration,
                    "view": "browser",
                    "action_offset": 0.5,
                    "voice_cue": action,
                    "expected_visible_state": "Actual generated Python source",
                }
                receipts.append(recorder.record_shot(lesson, shot))
    finally:
        lesson.close()
    (HERE / "codegen_capture.json").write_text(
        json.dumps(receipts, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
