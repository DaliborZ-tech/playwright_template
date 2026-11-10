"""Owned real Windows editor/browser/terminal activity and fresh test evidence."""

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from contextlib import ExitStack
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "video_course/production"))
import numpy as np  # noqa: E402
import pyperclip  # noqa: E402
from playwright.sync_api import expect  # noqa: E402
from pywinauto import Desktop  # noqa: E402
from record_course import ensure_demo, ensure_sources  # noqa: E402
from studio import (  # noqa: E402
    PYTHON,
    WORKSPACE,
    Studio,
    focus,
    gui,
    paste,
    recording_surface,
    win32con,
    win32gui,
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Session:
    def __init__(self, chapter):
        self.chapter = chapter
        self.take = f"take_{int(time.time())}"
        (ROOT / "video_course/recordings").mkdir(parents=True, exist_ok=True)
        ensure_sources()
        self.demo = ensure_demo()
        subprocess.run(
            [
                str(ROOT / ".venv/Scripts/python.exe"),
                str(ROOT / "video_course/production/open_studio.py"),
                "--workspace",
                str(WORKSPACE),
                "--full",
                "--enable-python",
            ],
            check=True,
        )
        self.studio = Studio(editor_title="Playwright Academy Studio Full", slow_mo=0)
        self.surfaces = ExitStack()
        self.handles = set()
        self.add(self.studio.editor)
        self.add(self.studio.browser_window)
        self.page = self.studio.page
        self.progress = {}
        self.created = "Regresní požadavek" if chapter == 8 else "Kontrola fakturace"
        self.dom_open = False
        self.runs = []
        self.codegen = None
        self.last_source = None
        self.stage = HERE / "chapters" / f"{chapter:02}"
        self.evidence = self.stage / "evidence" / self.take
        self.evidence.mkdir(parents=True, exist_ok=True)
        self.status = WORKSPACE / f"reports/terminal_full_{chapter:02}.json"
        self.studio.terminal("versions", f"full_{chapter:02}")
        gui.hotkey("ctrl", "c")
        time.sleep(0.25)
        self.studio.editor_file("training/solutions/test_01_open.py")

    def add(self, handle, preserve=False):
        if handle not in self.handles:
            if preserve:
                win32gui.SetWindowPos(
                    handle,
                    win32con.HWND_TOPMOST,
                    0,
                    0,
                    0,
                    0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
                )
            else:
                self.surfaces.enter_context(recording_surface(handle))
            self.handles.add(handle)
        return handle

    def browser(self):
        focus(self.studio.browser_window)
        if self.dom_open:
            gui.press("f12")
            time.sleep(0.3)
            self.dom_open = False

    def login(self, reset=False):
        self.browser()
        self.page.goto("http://127.0.0.1:5000/login")
        self.page.get_by_label("E-mail", exact=True).fill("tester@example.test")
        self.page.get_by_label("Heslo", exact=True).fill("Academy123!")
        self.page.get_by_role("button", name="Přihlásit se").click()
        expect(self.page.get_by_role("heading", name="Dashboard", exact=True)).to_be_visible()
        if reset:
            self.page.get_by_role("button", name="Obnovit výchozí data").click()
        return self.proof_browser(self.page.get_by_role("heading", name="Dashboard", exact=True))

    def ready(self):
        self.browser()
        if self.page.locator("#record-dialog[open]").count():
            self.page.get_by_role("button", name="Zrušit", exact=True).click()
        if self.page.url.endswith("/login") or self.page.url.startswith("file:"):
            self.login()
        if not self.page.url.endswith("/records"):
            self.page.goto("http://127.0.0.1:5000/records")

    def proof_browser(self, locator=None):
        proof = {
            "url": self.page.url,
            "headings": self.page.get_by_role("heading").all_text_contents(),
            "record_rows": self.page.get_by_test_id("record-row").count(),
        }
        if locator is not None:
            box = locator.first.bounding_box()
            viewport = self.page.evaluate("({width:innerWidth,height:innerHeight})")
            if box and box["height"] < viewport["height"] - 30:
                locator.first.scroll_into_view_if_needed()
                time.sleep(0.2)
                box = locator.first.bounding_box()
                if box["y"] < -1 or box["y"] + box["height"] > viewport["height"] + 1:
                    raise RuntimeError(
                        "Teaching target remains outside the actual browser viewport"
                    )
            geometry = self.page.evaluate(
                "({top:screenY+outerHeight-innerHeight,dpr:devicePixelRatio})"
            )
            if box:
                visible_y = max(0, box["y"])
                visible_bottom = min(viewport["height"], box["y"] + box["height"])
                proof["focus_rect"] = [
                    box["x"],
                    visible_y + geometry["top"] + 24,
                    box["width"],
                    max(0, visible_bottom - visible_y),
                ]
                proof["actual_dom_rect"] = box
                proof["visible_height_fraction"] = max(0, visible_bottom - visible_y) / max(
                    1, box["height"]
                )
            proof["target_outer_html"] = locator.first.evaluate("el=>el.outerHTML")
        return proof

    def code(self, source, pattern="", write=False):
        original = ROOT / source
        current = WORKSPACE / source
        content = (
            original.read_text(encoding="utf-8")
            if original.exists()
            else current.read_text(encoding="utf-8")
        )
        lines = content.splitlines(keepends=True)
        if pattern == "expect":
            pattern = "expect("
        matches = [i for i, text in enumerate(lines, 1) if pattern and pattern in text]
        if source == "tests/smoke/test_login.py" and pattern in {"expect(", "expect"}:
            heading = [i for i in matches if 'get_by_role("heading"' in lines[i - 1]]
            matches = heading or matches
        if pattern and not matches:
            raise ValueError(f"Missing semantic source anchor: {source}: {pattern}")
        line = matches[0] if matches else 1
        if source in self.progress and line > len(self.progress[source].splitlines()):
            write = True
        self.studio.editor_file(source, line)
        # The isolated production profile can retain an unsaved buffer after a
        # failed take. Restore the actual on-disk working file before teaching
        # from it; the owner's main IDE profile is never touched.
        gui.hotkey("ctrl", "shift", "p")
        time.sleep(0.25)
        paste("File: Revert File")
        gui.press("enter")
        time.sleep(0.35)
        gui.press("escape")
        if write:
            if source not in self.progress:
                gui.hotkey("ctrl", "a")
                gui.press("backspace")
                self.progress[source] = ""
            target = "".join(lines[: max(line, 3)])
            previous = self.progress[source]
            if not target.startswith(previous):
                target = content
            delta = target[len(previous) :]
            gui.hotkey("ctrl", "end")
            for part in delta.splitlines(keepends=True):
                paste(part.rstrip("\n"))
                if part.endswith("\n"):
                    gui.press("enter")
            gui.hotkey("ctrl", "s")
            deadline = time.monotonic() + 4
            while current.read_text(encoding="utf-8") != target and time.monotonic() < deadline:
                time.sleep(0.1)
            if current.read_text(encoding="utf-8") != target:
                (self.evidence / "editor_mismatch.json").write_text(
                    json.dumps(
                        {
                            "source": source,
                            "expected": target,
                            "actual": current.read_text(encoding="utf-8"),
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
                if win32gui.GetForegroundWindow() == self.studio.editor:
                    gui.screenshot().save(str(self.evidence / "editor_mismatch.png"))
                raise RuntimeError(f"Actual editor content differs in {source}")
            self.progress[source] = target
        visible = current.read_text(encoding="utf-8")
        line = min(line, max(1, len(visible.splitlines())))
        expected = visible.splitlines()[line - 1] if visible.splitlines() else ""
        selected = None
        for _ in range(3):
            gui.press("escape")
            gui.hotkey("ctrl", "g")
            time.sleep(0.25)
            gui.hotkey("ctrl", "a")
            paste(f":{line}")
            gui.press("enter")
            time.sleep(0.5)
            gui.hotkey("ctrl", "l")
            time.sleep(0.15)
            gui.hotkey("ctrl", "c")
            time.sleep(0.2)
            selected = pyperclip.paste().replace("\r\n", "\n")
            if selected.rstrip("\n") == expected:
                break
        if selected.rstrip("\n") != expected:
            raise RuntimeError(f"Real native selection differs: {selected!r} / {expected!r}")
        pixels = np.asarray(gui.screenshot()).astype(np.int16)
        mask = np.all(np.abs(pixels - np.array([39, 85, 107])) < 10, axis=2)
        mask[:, :350] = False
        mask[:85] = False
        mask[980:] = False
        ys, xs = np.nonzero(mask)
        rect = [430, 150, 1350, 500]
        if len(xs) > 100:
            rect = [
                int(xs.min()),
                int(ys.min()) + 24,
                int(xs.max() - xs.min()),
                int(ys.max() - ys.min()),
            ]
        self.last_source = source
        return {
            "file": source,
            "line": line,
            "actual_selected_text": selected,
            "source_sha256": sha(current),
            "matches_frozen_source": visible == content,
            "actual_text": visible,
            "focus_rect": rect,
            "native_editor_selection": True,
        }

    def restore(self):
        for source in list(self.progress):
            complete = (ROOT / source).read_text(encoding="utf-8")
            if (WORKSPACE / source).read_text(encoding="utf-8") != complete:
                self.studio.editor_file(source)
                gui.hotkey("ctrl", "a")
                paste(complete)
                gui.hotkey("ctrl", "s")
                time.sleep(0.2)
                assert (WORKSPACE / source).read_text(encoding="utf-8") == complete
        self.progress.clear()

    def terminal(self):
        focus(self.studio.editor)
        window = Desktop(backend="uia").window(handle=self.studio.editor)
        tabs = [
            t
            for t in window.descendants(control_type="TabItem")
            if t.window_text().startswith("Terminal")
        ]
        if not tabs:
            gui.hotkey("ctrl", "j")
        time.sleep(0.25)
        maximize = window.child_window(title="Maximize Panel", control_type="Button")
        if maximize.exists(timeout=0.2):
            maximize.click_input()
        gui.click(700, 220)

    def run(self, kind):
        if kind != "compile_bad":
            self.restore()
        ordinal = len(self.runs) + 1
        folder = WORKSPACE / f"reports/full/{self.take}/{self.chapter:02}/{ordinal:02}"
        folder.mkdir(parents=True, exist_ok=True)
        python = ".\\.venv\\Scripts\\python.exe"
        targets = {
            "regression": "-m regression",
            "smoke": "-m smoke",
            "visible": "-m smoke --headed --slowmo=250",
            "python": "training/solutions/test_03_python.py",
            "first": "tests/examples/test_video_created.py",
            "locators": "training/solutions/test_05_locators.py",
            "parametrize": "training/solutions/test_07_parametrize.py",
            "journey": (
                "tests/regression/test_records.py::test_12_complete_regression_journey "
                "--headed --slowmo=250"
            ),
            "refined": "training/solutions/test_09_codegen_refined.py",
            "search": "training/solutions/test_12_search.py",
            "selected": "training/solutions/test_11_report.py",
            "fixed": "training/solutions/test_10_fixed.py",
            "failure": "tests/teaching/test_expected_failure.py --teaching-failure",
        }
        commands = {
            "interpreter": python
            + ' -c "import sys; print(sys.version.split()[0]); print(sys.executable)"',
            "version": python + " --version",
            "setup": "scripts\\setup_windows.cmd",
            "pip_version": python + " -m pip --version",
            "pip_check": python + " -m pip check",
            "playwright_version": python + " -m playwright --version",
            "browser_install": python + " -m playwright install chromium",
            "compile_bad": python + " -m py_compile training/solutions/test_03_python.py",
            "python_values": python
            + (
                ' -c "from training.solutions.test_03_python import normalize; '
                "print(repr(normalize(' Kontrola exportu ')))\""
            ),
            "python_empty": python
            + (
                ' -c "from training.solutions.test_03_python import normalize; '
                "print(repr(normalize('   ')))\""
            ),
            "python_three": python
            + (
                ' -c "from training.solutions.test_03_python import normalize; '
                "print([normalize(v) for v in "
                "[' Kontrola exportu ', 'Kontrola fakturace', '   ']])\""
            ),
        }
        if kind in targets:
            relative = folder.relative_to(WORKSPACE).as_posix()
            command = (
                f"{python} -m pytest {targets[kind]} -q --html={relative}/report.html "
                f"--junitxml={relative}/junit.xml --output={relative}/artifacts --video=on "
                + ("--tracing=on" if kind == "failure" else "--tracing=off")
            )
        else:
            command = commands[kind]
        self.terminal()
        gui.hotkey("ctrl", "c")
        time.sleep(0.25)
        paste(command)
        started = time.time()
        gui.press("enter")
        deadline = time.monotonic() + 120
        data = None
        headed_windows = []
        observed_headed_handles = set()
        while time.monotonic() < deadline:
            if "--headed" in command:
                import psutil
                import win32process

                candidates = []
                win32gui.EnumWindows(
                    lambda handle, _, candidates=candidates: (
                        candidates.append(handle)
                        if win32gui.IsWindowVisible(handle)
                        and win32gui.GetClassName(handle) == "Chrome_WidgetWin_1"
                        and handle not in self.handles
                        and handle not in observed_headed_handles
                        else None
                    ),
                    None,
                )
                for handle in candidates:
                    try:
                        pid = win32process.GetWindowThreadProcessId(handle)[1]
                        chain = [psutil.Process(pid), *psutil.Process(pid).parents()]
                        parent = next(
                            (
                                p
                                for p in chain
                                if "pytest" in p.cmdline()
                                and any(
                                    str(folder.relative_to(WORKSPACE)).replace("\\", "/")
                                    in arg.replace("\\", "/")
                                    for arg in p.cmdline()
                                )
                            ),
                            None,
                        )
                        if parent is not None:
                            # This transient browser closes with pytest. Do not
                            # retain a cleanup callback for a dead/reused HWND.
                            win32gui.SetWindowPos(
                                handle,
                                win32con.HWND_TOPMOST,
                                0,
                                0,
                                0,
                                0,
                                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
                            )
                            focus(handle)
                            observed_headed_handles.add(handle)
                            headed_windows.append(
                                {
                                    "pid": pid,
                                    "pytest_pid": parent.pid,
                                    "window": handle,
                                    "actual_title": win32gui.GetWindowText(handle),
                                    "bounds": win32gui.GetWindowRect(handle),
                                }
                            )
                    except (psutil.Error, RuntimeError):
                        continue
            if self.status.exists() and self.status.stat().st_mtime >= started:
                candidate = json.loads(self.status.read_text(encoding="utf-8"))
                if candidate["exit_code"] != 777:
                    data = candidate
                    break
            time.sleep(0.2)
        if data is None:
            raise RuntimeError(f"Actual terminal command did not complete: {kind}")
        expected = 1 if kind in {"compile_bad", "failure"} else 0
        if "--headed" in command:
            if not headed_windows:
                raise RuntimeError("Headed test produced no proven visible owned browser")
            focus(self.studio.editor)
        if data["exit_code"] != expected:
            raise RuntimeError(f"Actual {kind} exit {data['exit_code']}, expected {expected}")
        proof = {
            "kind": kind,
            "command": command,
            "exit_code": data["exit_code"],
            "started_unix": started,
            "focus_rect": [370, 100, 1530, 700],
            "actual_headed_browser_windows": headed_windows,
        }
        if kind in targets:
            junit = folder / "junit.xml"
            assert junit.stat().st_mtime >= started
            tree = ET.parse(junit)
            cases = tree.findall(".//testcase")
            failures, errors, skipped = [
                tree.findall(".//" + name) for name in ("failure", "error", "skipped")
            ]
            if not cases or len(failures) != expected or errors or skipped:
                raise RuntimeError("Actual JUnit differs from the intended run")
            for suite in tree.iter("testsuite"):
                suite.attrib.pop("hostname", None)
            tree.write(junit, encoding="utf-8", xml_declaration=True)
            saved = self.evidence / f"run_{ordinal:02}_{kind}"
            shutil.copytree(folder, saved)
            proof.update(
                testcases=len(cases),
                failures=len(failures),
                errors=0,
                skipped=0,
                actual_cases=[c.attrib for c in cases],
                junit=str((saved / "junit.xml").relative_to(ROOT)),
                junit_sha256=sha(saved / "junit.xml"),
                report=str((saved / "report.html").relative_to(ROOT)),
                report_sha256=sha(saved / "report.html"),
                runtime_report=str(folder / "report.html"),
                runtime_junit=str(junit),
                artifacts=[str(p.relative_to(ROOT)) for p in saved.rglob("*") if p.is_file()],
            )
        self.runs.append(proof)
        return proof

    def act(self, action):
        if action.startswith("focus_code:"):
            prepared = self.focus_prepared
            assert prepared["action"] == action
            gui.hotkey("ctrl", "l")
            time.sleep(.15)
            gui.hotkey("ctrl", "c")
            time.sleep(.2)
            selected = pyperclip.paste().replace("\r\n", "\n")
            assert selected == prepared["proof"]["actual_selected_text"]
            return {**prepared["proof"], "selection_verified_during_capture": True,
                    "editor_opened_before_capture": True}
        if action.startswith("case_note:"):
            kind = action.split(":", 1)[1]
            source = f"reports/student_notes/ch{self.chapter:02}_manual_case.txt"
            path = WORKSPACE / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
            if self.chapter == 12:
                parts = [
                    "Předpoklad: přihlášená relace a tři výchozí požadavky.\n",
                    "Akce: vyhledat neexistujici-synteticky-pozadavek.\n",
                    "Očekávání: nula řádků a zpráva Žádné odpovídající záznamy.\n",
                ]
            else:
                parts = [
                    "Předpoklad: lokální portál je spuštěný.\n",
                    "Akce: otevřít /login.\n",
                    "Očekávání: viditelný nadpis Přihlášení.\n",
                ]
            count = {"precondition": 1, "action": 2, "expected": 3}[kind]
            self.studio.editor_file(source)
            gui.hotkey("ctrl", "a")
            paste("".join(parts[:count]))
            gui.hotkey("ctrl", "s")
            time.sleep(0.2)
            actual = path.read_text(encoding="utf-8")
            assert actual == "".join(parts[:count])
            saved_note = self.evidence / f"manual_case_{kind}.txt"
            shutil.copyfile(path, saved_note)
            return {
                "file": source,
                "actual_written_case": actual,
                "sha256": sha(path),
                "saved_source": str(saved_note.relative_to(ROOT)),
                "focus_rect": [430, 100, 1400, 300],
            }
        if action.startswith(("code:", "write:")):
            kind, source, pattern = action.split(":", 2)
            return self.code(source, pattern, kind == "write")
        if action.startswith("run:"):
            return self.run(action[4:])
        if action == "login_form":
            self.browser()
            self.studio.context.clear_cookies()
            self.page.goto("http://127.0.0.1:5000/login")
            return self.proof_browser(
                self.page.get_by_role("heading", name="Přihlášení", exact=True)
            )
        if action in {"login", "login_reset", "new_session"}:
            if action == "new_session":
                self.studio.context.clear_cookies()
            return self.login(action == "login_reset")
        if action == "bad_login":
            self.act("login_form")
            self.page.get_by_label("E-mail", exact=True).fill("tester@example.test")
            self.page.get_by_label("Heslo", exact=True).fill("nespravne-heslo")
            self.page.get_by_role("button", name="Přihlásit se").click()
            expect(self.page.get_by_role("alert")).to_be_visible()
            return self.proof_browser(self.page.get_by_role("alert"))
        if action in {"new_form", "create", "duplicate_record"}:
            self.ready()
            if action == "duplicate_record":
                self.created = "Kontrola přihlášení navíc"
            if self.page.get_by_role("row").filter(has_text=self.created).count():
                self.page.get_by_role("button", name="Obnovit výchozí data").click()
            self.page.get_by_role("button", name="Nový záznam").click()
            if action != "new_form":
                self.act("fill_record")
                return self.act("save_record")
            return self.proof_browser(self.page.get_by_label("Název požadavku"))
        if action == "fill_record":
            self.browser()
            if not self.page.get_by_label("Název požadavku").is_visible():
                self.act("new_form")
            self.page.get_by_label("Název požadavku").fill(self.created)
            self.page.get_by_label("Řešitel", exact=True).select_option(label="Petr")
            self.page.get_by_label("Prioritní").check()
            return self.proof_browser(self.page.get_by_label("Název požadavku"))
        if action == "save_record":
            self.browser()
            self.page.get_by_role("button", name="Uložit záznam").click()
            row = self.page.get_by_role("row").filter(has_text=self.created)
            expect(row).to_contain_text("Petr")
            expect(row).to_contain_text("Vysoká")
            return self.proof_browser(row)
        if action in {"scope_created", "update_reload", "delete_record", "cancel_delete"}:
            self.ready()
            row = self.page.get_by_role("row").filter(has_text=self.created)
            if row.count() == 0:
                self.act("create")
            if action == "update_reload":
                row.get_by_role("button", name="Upravit " + self.created, exact=True).click()
                self.page.get_by_label("Stav", exact=True).select_option(label="Hotový")
                self.page.get_by_role("button", name="Uložit záznam").click()
                self.page.reload()
                expect(row).to_contain_text("Hotový")
            elif action in {"delete_record", "cancel_delete"}:

                def dialog_response(dialog):
                    time.sleep(1)
                    dialog.accept() if action == "delete_record" else dialog.dismiss()

                self.page.once("dialog", dialog_response)
                row.get_by_role("button", name="Smazat " + self.created, exact=True).click()
                expect(row).to_have_count(0 if action == "delete_record" else 1)
                return self.proof_browser(self.page.get_by_role("table"))
            row.evaluate("el=>el.style.outline='3px solid #21a366'")
            return self.proof_browser(row)
        if action == "reload":
            self.browser()
            self.page.reload()
            return self.proof_browser(self.page.get_by_role("table"))
        if action in {"scope_row", "scope_exact"}:
            self.ready()
            row = self.page.get_by_role("row").filter(has_text="Kontrola přihlášení")
            if action == "scope_exact":
                row = self.page.get_by_test_id("record-row").filter(
                    has=self.page.get_by_role(
                        "button", name="Upravit Kontrola přihlášení", exact=True
                    )
                )
            for item in row.all():
                item.evaluate("el=>el.style.outline='3px solid #21a366'")
            return {
                **self.proof_browser(row),
                "selected_rows": row.count(),
                "teaching_outline_only": True,
            }
        if action in {"search", "empty_search", "scope_empty"}:
            self.ready()
            field = self.page.get_by_label("Vyhledat záznam")
            field.fill("neexistujici-synteticky-pozadavek" if action != "search" else "Export")
            expect(self.page.get_by_test_id("record-row")).to_have_count(
                1 if action == "search" else 0
            )
            return self.proof_browser(
                field
                if action != "scope_empty"
                else self.page.get_by_text("Žádné odpovídající záznamy.", exact=True)
            )
        if action == "logout":
            self.ready()
            self.page.get_by_role("button", name="Odhlásit se", exact=True).click()
            self.page.goto("http://127.0.0.1:5000/records")
            expect(self.page.get_by_role("heading", name="Přihlášení", exact=True)).to_be_visible()
            return self.proof_browser(
                self.page.get_by_role("heading", name="Přihlášení", exact=True)
            )
        if action in {"api_error", "recover"}:
            self.ready()
            if action == "api_error":
                if self.page.locator("#api-error").is_visible():
                    self.page.get_by_role("button", name="Načíst znovu", exact=True).click()
                    expect(self.page.locator("#loading")).to_be_hidden()
                    expect(self.page.locator("#api-error")).to_be_hidden()
                self.recovery_row_count = self.page.get_by_test_id("record-row").count()
                if self.page.locator("details.teaching-tools").get_attribute("open") is None:
                    self.page.get_by_text("Výukové nástroje", exact=True).click()
                self.page.get_by_role("button", name="Simulovat chybu API").click()
                expect(self.page.get_by_role("alert")).to_contain_text("503")
                return self.proof_browser(self.page.get_by_role("alert"))
            self.page.get_by_role("button", name="Načíst znovu", exact=True).click()
            expect(self.page.get_by_test_id("record-row")).to_have_count(self.recovery_row_count)
            return self.proof_browser(self.page.get_by_role("table"))
        if action in {"report", "report_failure", "junit"}:
            run = (
                next((r for r in reversed(self.runs) if r.get("kind") == "failure"), None)
                if action == "report_failure"
                else next((r for r in reversed(self.runs) if "report" in r), None)
            )
            if run is None:
                run = self.run("failure" if action == "report_failure" else "smoke")
            if action == "junit":
                return self.code(str(Path(run["runtime_junit"]).relative_to(WORKSPACE)), "testcase")
            self.browser()
            self.page.goto(Path(run["runtime_report"]).as_uri())
            self.page.get_by_text("Summary", exact=True).wait_for()
            return {**self.proof_browser(self.page.locator("#results-table")), "run": run}
        if action == "interpreter":
            self.studio.editor_file("tests/smoke/test_login.py")
            gui.hotkey("ctrl", "shift", "p")
            time.sleep(0.3)
            paste("Python: Select Interpreter")
            gui.press("enter")
            time.sleep(1.2)
            window = Desktop(backend="uia").window(handle=self.studio.editor)
            choices = window.descendants(control_type="ListItem")
            labels = [item.window_text() for item in choices]
            selected = next(
                (
                    item
                    for item in choices
                    if ".venv" in item.window_text() and "3.12" in item.window_text()
                ),
                None,
            )
            if selected is None:
                raise RuntimeError(
                    f"Project interpreter absent from actual native picker: {labels}"
                )
            chosen = selected.window_text()
            selected.click_input()
            time.sleep(0.5)
            result = self.run("interpreter")
            return {
                "interpreter": str(PYTHON),
                "native_picker_choices": labels,
                "selected_native_picker_item": chosen,
                "run": result,
                "method": "Native interpreter selection and actual explicit-path Python diagnostic",
            }
        if action == "restore_python":
            source = "training/solutions/test_03_python.py"
            self.studio.editor_file(source)
            gui.hotkey("ctrl", "a")
            paste((ROOT / source).read_text(encoding="utf-8"))
            gui.hotkey("ctrl", "s")
            self.progress.pop(source, None)
            return self.code(source, "if not")
        if action == "syntax_break":
            self.restore()
            source = "training/solutions/test_03_python.py"
            self.code(source, "cleaned =")
            paste("cleaned = title.strip()\n")
            gui.hotkey("ctrl", "s")
            time.sleep(0.2)
            return {
                "file": source,
                "actual_text": (WORKSPACE / source).read_text(encoding="utf-8"),
                "source_sha256": sha(WORKSPACE / source),
                "intended_syntax_error": True,
            }
        if action == "invalid_form":
            self.act("new_form")
            self.page.get_by_label("Název požadavku").fill("ab")
            self.page.get_by_role("button", name="Uložit záznam").click()
            error = self.page.locator("#form-error")
            expect(error).to_contain_text("3 až 80")
            return self.proof_browser(error)
        if action in {"inspect_email", "inspect_header", "inspect_row"}:
            return self.inspect(action)
        if action in {"trace", "trace_navigation", "trace_snapshot", "failure_screenshot", "debug"}:
            return self.diagnostics(action)
        if action in {"codegen_record", "codegen_inspect", "codegen_source"}:
            return self.codegen_action(action)
        raise ValueError(f"Unsupported real action: {action}")

    def inspect(self, action):
        self.browser()
        if action == "inspect_email":
            self.act("login_form")
            target = self.page.get_by_label("E-mail", exact=True)
        else:
            self.ready()
            target = (
                self.page.locator("thead tr")
                if action == "inspect_header"
                else self.page.get_by_test_id("record-row").first
            )
        gui.press("f12")
        time.sleep(0.6)
        self.dom_open = True
        gui.hotkey("ctrl", "shift", "c")
        time.sleep(0.2)
        box = target.bounding_box()
        geometry = self.page.evaluate("({y:screenY+outerHeight-innerHeight,dpr:devicePixelRatio})")
        gui.click(
            round(box["x"] + box["width"] / 2),
            round(geometry["y"] + box["y"] + box["height"] / 2 - 7),
        )
        time.sleep(0.3)
        proof = self.proof_browser(target)
        window = Desktop(backend="uia").window(handle=self.studio.browser_window)
        selected = []
        for item in window.descendants(control_type="TreeItem"):
            try:
                if item.is_selected():
                    selected.append(item.window_text())
            except Exception:
                if item.legacy_properties().get("State", 0) & 2:
                    selected.append(item.window_text())
        if not selected:
            raise RuntimeError("Native DevTools did not prove a selected DOM row")
        return {**proof, "actual_devtools_selection": selected, "focus_rect": [1370, 200, 530, 600]}

    def diagnostics(self, action):
        if action == "debug":
            handle, callback = self.studio.debug()
            self.add(handle)
            callback()
            return {"method": "Real PWDEBUG Inspector and actual user-code stepping"}
        failure = next((r for r in reversed(self.runs) if r["kind"] == "failure"), None)
        if failure is None:
            failure = self.run("failure")
        if action == "failure_screenshot":
            png = next((ROOT / Path(failure["junit"]).parent).rglob("*.png"))
            self.browser()
            self.page.goto(png.as_uri())
            return {"actual_failure_screenshot": str(png.relative_to(ROOT)), "sha256": sha(png)}
        traces = list(
            (WORKSPACE / f"reports/full/{self.take}/{self.chapter:02}").rglob("trace.zip")
        )
        if not getattr(self, "trace_url", None):
            driver = PYTHON.parents[1] / "Lib/site-packages/playwright/driver"
            log_path = self.evidence / "trace-server.log"
            log = log_path.open("w", encoding="utf-8")
            self.studio.trace_process = subprocess.Popen(
                [
                    str(driver / "node.exe"),
                    str(HERE / "open_trace.cjs"),
                    str(driver / "package/lib/coreBundle.js"),
                    str(traces[-1]),
                ],
                cwd=WORKSPACE,
                stdout=log,
                stderr=log,
            )
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                text = log_path.read_text(encoding="utf-8")
                match = re.search(r"http://127\.0\.0\.1:\d+", text)
                if match:
                    self.trace_url = match[0]
                    break
                time.sleep(0.2)
            else:
                raise RuntimeError(f"Official trace server did not start: {text}")
        self.browser()
        if not self.page.url.startswith(self.trace_url):
            self.page.goto(self.trace_url)
        failed = self.page.get_by_text('Expect "to_be_visible"', exact=True)
        failed.wait_for()
        selected_controls = []
        if action in {"trace_navigation", "trace_snapshot"}:
            navigation = self.page.get_by_text("Navigate", exact=True)
            navigation.click()
            selected_controls.append(
                {
                    "text": "Navigate",
                    "actual_dom": navigation.locator("..").evaluate("el=>el.outerHTML"),
                }
            )
        else:
            failed.click()
            selected_controls.append(
                {
                    "text": failed.inner_text(),
                    "actual_dom": failed.locator("..").evaluate("el=>el.outerHTML"),
                }
            )
        if action == "trace_snapshot":
            for name in ("Before", "After"):
                item = self.page.get_by_text(name, exact=True)
                item.click()
                time.sleep(0.6)
                selected_controls.append(
                    {"text": name, "actual_dom": item.locator("..").evaluate("el=>el.outerHTML")}
                )
        return {
            "actual_trace": str(traces[-1]),
            "sha256": sha(traces[-1]),
            "official_trace_viewer": True,
            "presentation": "Installed Playwright Trace Viewer in an owned headed browser",
            "action": action,
            "selected_native_controls": selected_controls,
        }

    def codegen_action(self, action):
        if self.codegen is None:
            spec = importlib.util.spec_from_file_location(
                "full_codegen", ROOT / "video_course/r21/capture_codegen.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            module.HERE = self.evidence / "codegen"
            module.HERE.mkdir(parents=True, exist_ok=True)
            self.codegen = module.Codegen()
            self.add(self.codegen.browser, preserve=True)
            self.add(self.codegen.inspector, preserve=True)
        if action == "codegen_record":
            self.codegen.prepare({"on_screen_action": "cg_open"})
            self.codegen.act("cg_open")
            proof = self.codegen.act("cg_fill")
            gui.click(600, 805)
            paste("Academy123!")
            gui.click(600, 876)
            time.sleep(0.8)
            text = self.codegen.draft.read_text(encoding="utf-8")
            if not any(
                f'get_by_role("button", name="{label}").click()' in text
                for label in ("Přihlásit se", "Přihlásit se →")
            ):
                raise RuntimeError("Actual Codegen did not record the login button")
            destination = self.evidence / "original_codegen_draft.py"
            shutil.copyfile(self.codegen.draft, destination)
            self.generated_source = destination
            return {
                **proof,
                "actual_generated_text": text,
                "generated_source": str(destination.relative_to(ROOT)),
                "sha256": sha(destination),
            }
        if action == "codegen_inspect":
            self.codegen.prepare({"on_screen_action": "cg_inspector"})
            return self.codegen.act("cg_inspector")
        source = "tests/examples/codegen_draft.py"
        destination = WORKSPACE / source
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.touch(exist_ok=True)
        self.studio.editor_file(source)
        gui.hotkey("ctrl", "a")
        paste(self.generated_source.read_text(encoding="utf-8"))
        gui.hotkey("ctrl", "s")
        deadline = time.monotonic() + 5
        while sha(destination) != sha(self.generated_source) and time.monotonic() < deadline:
            time.sleep(0.1)
        assert sha(destination) == sha(self.generated_source)
        return {
            "file": source,
            "actual_generated_sha256": sha(WORKSPACE / source),
            "matches_original_export": sha(WORKSPACE / source) == sha(self.generated_source),
        }

    def close(self):
        self.surfaces.close()
        if self.codegen:
            self.codegen.close()
        self.studio.close()
        if self.demo:
            self.demo.terminate()
        ensure_sources()
