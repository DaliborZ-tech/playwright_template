"""Skutečné Windows aplikace a FFmpeg recording jejich oken. Bez falešných výstupů."""

import ctypes
import json
import os
import site
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEDIA = ROOT / ".tools/media-env/Lib/site-packages"
site.addsitedir(str(MEDIA))
sys.path.insert(0, str(ROOT))

import imageio_ffmpeg  # noqa: E402
import pyautogui as gui  # noqa: E402
import pyperclip  # noqa: E402
import win32api  # noqa: E402
import win32con  # noqa: E402
import win32gui  # noqa: E402
import win32process  # noqa: E402
from playwright.sync_api import expect, sync_playwright  # noqa: E402

WORKSPACE = Path("C:/QA/PlaywrightAcademy")
PYTHON = WORKSPACE / ".venv/Scripts/python.exe"
OUTPUT = ROOT / "video_course/recordings"


def wait_until(check, timeout=30):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = check()
        if value:
            return value
        time.sleep(0.2)
    raise TimeoutError("Požadované skutečné okno nebo výsledek se neobjevil.")


def window_with(fragment, exclude=()):
    result = []

    def collect(handle, _):
        if handle not in exclude and win32gui.IsWindowVisible(handle):
            if fragment in win32gui.GetWindowText(handle):
                result.append(handle)

    win32gui.EnumWindows(collect, None)
    return result[0] if result else None


def focus(handle, maximize=True):
    # Obnovený profil si může pamatovat druhý monitor. Natáčecí plocha je primární.
    work = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))["Work"]
    rect = win32gui.GetWindowRect(handle)
    center = ((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2)
    if not (work[0] <= center[0] < work[2] and work[1] <= center[1] < work[3]):
        win32gui.ShowWindow(handle, win32con.SW_RESTORE)
        win32gui.SetWindowPos(
            handle, win32con.HWND_TOP, work[0], work[1], work[2] - work[0], work[3] - work[1], 0
        )
    if win32gui.IsIconic(handle):
        win32gui.ShowWindow(handle, win32con.SW_RESTORE)
    if maximize and not ctypes.windll.user32.IsZoomed(handle):
        win32gui.ShowWindow(handle, win32con.SW_MAXIMIZE)
    try:
        win32gui.SetForegroundWindow(handle)
    except Exception:
        gui.press("alt")
        win32gui.SetForegroundWindow(handle)
    time.sleep(0.35)  # Produkční čas na přepnutí okna, nikoliv čekání UI testu.


def tool_windows(title):
    """Seznam již otevřených nástrojů; jejich neznámý původ neopravňuje k zavření."""
    handles = []
    win32gui.EnumWindows(
        lambda handle, _: (
            handles.append(handle)
            if win32gui.IsWindowVisible(handle) and title in win32gui.GetWindowText(handle)
            else None
        ),
        None,
    )
    return tuple(handles)


def paste(value):
    pyperclip.copy(value)
    gui.hotkey("ctrl", "v")
    time.sleep(0.15)


def owns_foreground(handle):
    foreground = win32gui.GetForegroundWindow()
    return foreground == handle or (
        foreground and win32gui.GetAncestor(foreground, win32con.GA_ROOTOWNER) == handle
    )


@contextmanager
def recording_surface(handle, enabled=True):
    """Pouze řízené okno je dočasně topmost; původní příznak se vždy obnoví."""
    if not enabled:
        yield
        return
    was_topmost = bool(
        win32gui.GetWindowLong(handle, win32con.GWL_EXSTYLE) & win32con.WS_EX_TOPMOST
    )
    flags = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
    win32gui.SetWindowPos(handle, win32con.HWND_TOPMOST, 0, 0, 0, 0, flags)
    try:
        focus(handle)
        if not owns_foreground(handle):
            raise RuntimeError("Natáčecí okno není ověřeně v popředí.")
        yield
    finally:
        if win32gui.IsWindow(handle) and not was_topmost:
            win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, flags)


class Studio:
    def __init__(self, editor_title="Playwright Academy Studio", slow_mo=450):
        ctypes.windll.user32.SetProcessDPIAware()
        # VS Code při změně spouštěcích přepínačů nahrazuje původní hwnd.
        time.sleep(3)
        self.editor = wait_until(lambda: window_with(editor_title), timeout=60)
        focus(self.editor)
        # Vlastní oddělený profil může při prvním otevření zobrazit přihlášení.
        gui.press("escape")
        gui.click(1080, 700)
        gui.press("escape")
        for command in ("View: Reset Zoom", "View: Close Panel"):
            gui.hotkey("ctrl", "shift", "p")
            time.sleep(0.3)
            paste(command)
            gui.press("enter")
            time.sleep(0.4)
        self.terminal_open = False
        self.codegen_process = None
        self.trace_process = None
        self.trace_window = None
        self.inspector_process = None
        self.debug_window = None
        self.inspector = None
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(
            headless=False,
            slow_mo=slow_mo,
            args=["--start-maximized", "--force-renderer-accessibility"],
        )
        self.context = self.browser.new_context(no_viewport=True, locale="cs-CZ")
        self.page = self.context.new_page()
        self.page.goto("http://127.0.0.1:5000/login")
        session = self.browser.new_browser_cdp_session()
        browser_pid = int(
            next(
                p["id"]
                for p in session.send("SystemInfo.getProcessInfo")["processInfo"]
                if p["type"] == "browser"
            )
        )

        def owned_browser_window():
            matches = []
            win32gui.EnumWindows(
                lambda h, _: (
                    matches.append(h)
                    if win32gui.IsWindowVisible(h)
                    and win32process.GetWindowThreadProcessId(h)[1] == browser_pid
                    else None
                ),
                None,
            )
            return matches[0] if matches else None

        self.browser_window = wait_until(owned_browser_window)
        focus(self.browser_window)
        python = ".\\.venv\\Scripts\\python.exe"
        pytest = python + " -m pytest "
        self.commands = {
            "versions": python + " --version",
            "setup": "scripts\\setup_windows.cmd",
            "regression": pytest + "-m regression -q",
            "python": pytest + "training/solutions/test_03_python.py -q",
            "first": pytest + "tests/examples/test_video_created.py -q",
            "parametrize": pytest + "training/solutions/test_07_parametrize.py -q",
            "journey": pytest + "tests/regression/test_records.py::"
            "test_12_complete_regression_journey -q --headed --slowmo=200",
            "refined": pytest + "training/solutions/test_09_codegen_refined.py -q",
            "failure": "scripts\\run_failure.cmd",
            "fixed": "scripts\\run_fixed.cmd",
            "search": pytest + "training/solutions/test_12_search.py -q",
        }

    def editor_file(self, path, line=1):
        focus(self.editor)
        from pywinauto import Desktop

        own_window = Desktop(backend="uia").window(handle=self.editor)
        close_panel = own_window.child_window(title="Close Panel", control_type="Button")
        if close_panel.exists(timeout=0.5):
            close_panel.click_input()
        self.terminal_open = False
        gui.hotkey("ctrl", "p")
        time.sleep(0.35)
        paste(path.replace("\\", "/") + f":{line}")
        gui.press("enter")
        time.sleep(0.6)
        gui.press("escape")
        gui.moveTo(100, 220, duration=0.3)
        return self.editor

    def terminal(self, action, scene_id):
        focus(self.editor)
        # Příkazová paleta je nezávislá na českém rozložení klávesnice;
        # klávesová zkratka se zpětným apostrofem na něm terminál neotevřela.
        gui.hotkey("ctrl", "shift", "p")
        time.sleep(0.35)
        paste("Terminal: Create New Terminal")
        gui.press("enter")
        self.terminal_open = True
        time.sleep(2)
        from pywinauto import Desktop

        own_window = Desktop(backend="uia").window(handle=self.editor)
        maximize = own_window.child_window(title="Maximize Panel", control_type="Button")
        if maximize.exists(timeout=2):
            maximize.click_input()
        tabs = own_window.descendants(control_type="TabItem")
        terminal_tabs = [tab for tab in tabs if tab.window_text().startswith("Terminal")]
        if not terminal_tabs or terminal_tabs[0].rectangle().top > 150:
            raise RuntimeError("Nelze ověřit maximalizovaný panel skutečného terminálu.")
        gui.hotkey("ctrl", "shift", "p")
        time.sleep(0.25)
        paste("Notifications: Clear All Notifications")
        gui.press("enter")
        time.sleep(0.3)
        gui.click(700, 220)
        # Prompt se spustí až po dokončení skutečného příkazu. Uloží reálný
        # LASTEXITCODE mimo obraz; na obrazovce je běžný příkaz bez wrapperu.
        status_path = WORKSPACE / "reports" / f"terminal_{scene_id}.json"
        status_path.parent.mkdir(exist_ok=True)
        setup = (
            "$global:LASTEXITCODE=777; "
            "function global:prompt { $r=@{exit_code=$global:LASTEXITCODE; "
            f"scene='{scene_id}'; utc=[DateTime]::UtcNow.ToString('o')}}; "
            f"[IO.File]::WriteAllText('{status_path}',($r | ConvertTo-Json -Compress)); "
            "'PS Academy> ' }; Set-Location 'C:\\QA\\PlaywrightAcademy'; Clear-Host"
        )
        setup_started = time.time()
        paste(setup)
        gui.press("enter")
        wait_until(
            lambda: status_path.exists() and status_path.stat().st_mtime >= setup_started,
            timeout=60,
        )
        paste(self.commands[action])
        gui.moveTo(120, 210, duration=0.25)
        return self.editor, lambda: gui.press("enter")

    def interpreter_selection(self):
        """Skutečný příkaz v paletě a skutečný interpreter v terminálovém REPL."""
        from pywinauto import Desktop

        self.editor_file("tests/smoke/test_login.py")
        own_window = Desktop(backend="uia").window(handle=self.editor)
        expected = str(PYTHON)
        diagnostic = "import sys; print(sys.version.split()[0]); print(sys.executable)"

        def command(name):
            gui.hotkey("ctrl", "shift", "p")
            time.sleep(0.3)
            paste(name)
            gui.press("enter")

        def terminal_buffer():
            if not any(
                item.window_text().startswith("Terminal")
                for item in own_window.descendants(control_type="TabItem")
            ):
                return ""
            command("Terminal: Select All")
            gui.hotkey("ctrl", "shift", "c")
            time.sleep(0.25)
            value = pyperclip.paste()
            gui.press("escape")
            return value

        def verified_buffer():
            value = terminal_buffer()
            valid = "3.12.15" in value and any(
                line.strip().casefold() == expected.casefold() for line in value.splitlines()
            )
            return value if valid else False

        # Studený PowerShell/REPL se připraví mimo záznam, nikoli v tichu
        # během komentáře. Ve videu pak skutečný diagnostický příkaz zopakujeme.
        command("Python: Start Terminal REPL")
        self.terminal_open = True
        wait_until(lambda: ">>>" in terminal_buffer(), timeout=60)
        paste(diagnostic)
        gui.press("enter")
        wait_until(verified_buffer, timeout=20)
        command("Terminal: Clear")
        self.editor_file("tests/smoke/test_login.py")

        def show_palette():
            gui.hotkey("ctrl", "shift", "p")
            time.sleep(0.3)
            paste("Python: Select Interpreter")

        show_palette()
        wait_until(
            lambda: any(
                "Python: Select Interpreter" in item.window_text()
                for item in own_window.descendants(control_type="ListItem")
            ),
            timeout=45,
        )

        def show_repl():
            gui.press("escape")
            gui.hotkey("ctrl", "j")
            time.sleep(0.5)
            maximize = own_window.child_window(title="Maximize Panel", control_type="Button")
            if maximize.exists(timeout=2):
                maximize.click_input()
            gui.click(720, 250)
            paste(diagnostic)
            gui.press("enter")
            time.sleep(1)
            buffer = wait_until(verified_buffer, timeout=15)
            if "C:\\Users\\" in buffer or "3.12.15" not in buffer:
                raise RuntimeError("REPL nemá ověřenou verzi nebo obsahuje osobní cestu.")
            proof = {
                "method": "Configured default, actual command palette and terminal REPL",
                "selected_executable": expected,
                "actual_terminal_buffer": buffer,
                "python_version": "3.12.15",
            }
            (ROOT / "evidence/interpreter-selection.json").write_text(
                json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            gui.press("escape")
            self.terminal_open = True

        return self.editor, [(8, show_repl)]

    def login(self):
        page = self.page
        self.context.clear_cookies()
        page.goto("http://127.0.0.1:5000/login")
        page.get_by_label("E-mail", exact=True).fill("tester@example.test")
        page.get_by_label("Heslo", exact=True).fill("Academy123!")
        page.get_by_role("button", name="Přihlásit se").click()
        expect(page.get_by_role("heading", name="Dashboard", exact=True)).to_be_visible()
        expect(page.get_by_test_id("record-row")).to_have_count(3)

    def reset(self):
        if not self.page.url.endswith(("/dashboard", "/records")):
            self.login()
        self.page.get_by_role("button", name="Obnovit výchozí data").click()
        expect(self.page.get_by_test_id("record-row")).to_have_count(3)

    def browser_action(self, action):
        page = self.page
        focus(self.browser_window)
        if action == "report":
            page.goto((WORKSPACE / "reports/report.html").as_uri())
            return
        if action in {"overview", "login"}:
            # Nový context dává stejné deterministické tři seed záznamy.
            self.context.clear_cookies()
            self.login()
            return
        if action in {"create", "journey"}:
            self.reset()
            page.get_by_role("button", name="Nový záznam").click()
            page.get_by_label("Název požadavku").fill("Kontrola fakturace")
            page.get_by_label("Řešitel", exact=True).select_option(label="Petr")
            page.get_by_label("Prioritní").check()
            page.get_by_role("button", name="Uložit záznam").click()
            row = page.get_by_role("row").filter(has_text="Kontrola fakturace")
            expect(row).to_contain_text("Petr")
            if action == "journey":
                row.get_by_role("button", name="Upravit Kontrola fakturace", exact=True).click()
                page.get_by_label("Stav", exact=True).select_option(label="Hotový")
                page.get_by_role("button", name="Uložit záznam").click()
                expect(row).to_contain_text("Hotový")
                page.once("dialog", lambda dialog: dialog.accept())
                row.get_by_role("button", name="Smazat Kontrola fakturace", exact=True).click()
                expect(row).to_have_count(0)
            return
        self.reset()
        if action == "search":
            page.get_by_label("Vyhledat záznam").fill("Export")
            expect(page.get_by_test_id("record-row")).to_have_count(1)
        elif action == "empty":
            page.get_by_label("Vyhledat záznam").fill("neexistujici-synteticky-pozadavek")
            expect(page.get_by_text("Žádné odpovídající záznamy.", exact=True)).to_be_visible()
        elif action == "api_error":
            page.get_by_text("Výukové nástroje", exact=True).click()
            page.get_by_role("button", name="Simulovat chybu API").click()
            expect(page.get_by_role("alert")).to_contain_text("503")

    def close(self):
        for handle in (self.trace_window, self.debug_window, self.inspector):
            if handle and win32gui.IsWindow(handle):
                win32gui.PostMessage(handle, win32con.WM_CLOSE, 0, 0)
        for process in (self.codegen_process, self.trace_process, self.inspector_process):
            if process and process.poll() is None:
                process.terminate()
        self.browser.close()
        self.pw.stop()

    def codegen(self, inspect=False):
        if self.codegen_process is None or self.codegen_process.poll() is not None:
            log = (OUTPUT / "codegen-process.log").open("w", encoding="utf-8")
            self.codegen_process = subprocess.Popen(
                [
                    str(PYTHON),
                    "-m",
                    "playwright",
                    "codegen",
                    "--target=python-pytest",
                    "--viewport-size=1600,900",
                    "--output=tests/examples/codegen_draft.py",
                    "http://127.0.0.1:5000/login",
                ],
                cwd=WORKSPACE,
                stdout=log,
                stderr=log,
            )
            self.inspector = wait_until(lambda: window_with("Playwright Inspector"), timeout=45)
            self.codegen_window = wait_until(
                lambda: window_with("Playwright Academy", (self.editor, self.browser_window)),
                timeout=45,
            )
        if inspect:
            focus(self.inspector)
            gui.press("escape")
            gui.hotkey("ctrl", "0")
            gui.keyDown("ctrl")
            gui.press("add", presses=3, interval=0.15)
            gui.keyUp("ctrl")
            return self.inspector, lambda: gui.moveTo(450, 280, duration=1)
        focus(self.codegen_window)
        return self.codegen_window, self.record_codegen_login

    def record_codegen_login(self):
        # Toto jsou skutečné klávesové interakce v Codegen browseru.
        gui.hotkey("ctrl", "l")
        paste("http://127.0.0.1:5000/login")
        gui.press("enter")
        time.sleep(2)
        gui.press("tab", presses=4, interval=0.3)
        paste("tester@example.test")
        gui.press("tab")
        paste("Academy123!")
        gui.press("tab")
        gui.press("enter")
        time.sleep(2)

    def trace(self, trace_path=None):
        traces = (
            [Path(trace_path)]
            if trace_path
            else list((WORKSPACE / "reports/failure-artifacts").rglob("trace.zip"))
        )
        if not traces:
            raise RuntimeError("Trace neexistuje. Nejprve musí skutečně selhat výukový test.")
        if self.trace_process is None or self.trace_process.poll() is not None:
            prior_windows = tool_windows("Playwright Trace Viewer")
            log = (OUTPUT / "trace-process.log").open("w", encoding="utf-8")
            self.trace_process = subprocess.Popen(
                [str(PYTHON), "-m", "playwright", "show-trace", str(traces[0])],
                cwd=WORKSPACE,
                stdout=log,
                stderr=log,
            )
            self.trace_window = wait_until(
                lambda: window_with("Playwright Trace Viewer", prior_windows), timeout=45
            )
        handle = self.trace_window
        time.sleep(2)
        focus(handle)
        gui.press("escape")
        gui.hotkey("ctrl", "0")
        gui.keyDown("ctrl")
        gui.press("add", presses=2, interval=0.15)
        gui.keyUp("ctrl")

        def select_failed_expect():
            import numpy as np

            # Skutečný červený řádek selhání ve vlastním Trace Vieweru.
            # Nepoužíváme souřadnici, která po zoomu ukazovala na Create page.
            focus(handle)
            if win32gui.GetForegroundWindow() != handle:
                raise RuntimeError("Trace Viewer není v popředí.")
            left, top, right, bottom = win32gui.GetWindowRect(handle)
            left, top = max(0, left), max(0, top)
            image = gui.screenshot(
                region=(left, top + 100, min(450, right - left), min(550, bottom - top - 100))
            )
            pixels = np.asarray(image).astype(np.float32)
            red = (
                (pixels[:, :, 0] > 60)
                & (pixels[:, :, 0] > pixels[:, :, 1] * 1.5)
                & (pixels[:, :, 0] > pixels[:, :, 2] * 1.3)
            )
            rows = np.flatnonzero(red.sum(axis=1) > 8)
            if not len(rows):
                raise RuntimeError("Nenalezen skutečný červený řádek chybného očekávání.")
            groups = np.split(rows, np.where(np.diff(rows) > 1)[0] + 1)
            group = max(groups, key=len)
            if len(group) < 8:
                raise RuntimeError("Nejednoznačný řádek chyby v Trace Vieweru.")
            y = int((group[0] + group[-1]) / 2)
            columns = np.flatnonzero(red[y])
            x = int((columns[0] + columns[-1]) / 2)
            gui.click(left + x, top + 100 + y)
            gui.moveTo(left + 500, top + 180, duration=0.3)

        return handle, select_failed_expect

    def debug(self):
        if self.inspector_process is None or self.inspector_process.poll() is not None:
            prior_windows = tool_windows("Playwright Inspector")
            environment = {**os.environ, "PWDEBUG": "1", "PYTHONUTF8": "1"}
            log = (OUTPUT / "inspector-process.log").open("w", encoding="utf-8")
            self.inspector_process = subprocess.Popen(
                [
                    str(PYTHON),
                    "-m",
                    "pytest",
                    "tests/examples/test_first_test.py",
                    "-s",
                    "--output=reports/inspector-artifacts",
                    "--html=reports/inspector.html",
                    "--junitxml=reports/inspector.xml",
                    "--tracing=off",
                    "--screenshot=off",
                    "--video=off",
                ],
                cwd=WORKSPACE,
                env=environment,
                stdout=log,
                stderr=log,
            )
            self.debug_window = wait_until(
                lambda: window_with("Playwright Inspector", prior_windows), timeout=45
            )
        handle = self.debug_window
        time.sleep(2)
        focus(handle)
        gui.press("escape")
        gui.hotkey("ctrl", "0")
        gui.keyDown("ctrl")
        gui.press("add", presses=5, interval=0.15)
        gui.keyUp("ctrl")
        time.sleep(2)
        gui.press("escape")

        def step_user_code():
            gui.press("escape")
            gui.press("f10")

        return handle, step_user_code


def ffmpeg():
    return imageio_ffmpeg.get_ffmpeg_exe()


def record_window(handle, audio, destination, duration):
    destination.parent.mkdir(parents=True, exist_ok=True)
    log = destination.with_suffix(".ffmpeg.log").open("w", encoding="utf-8")
    # GDI snímání samotného GPU okna vrací černé pixely. Snímáme jeho skutečnou
    # viditelnou oblast desktopu, oříznutou na vlastní okno a pracovní plochu.
    work = win32api.GetMonitorInfo(win32api.MonitorFromWindow(handle))["Work"]
    rect = win32gui.GetWindowRect(handle)
    left, top = max(work[0], rect[0]), max(work[1], rect[1])
    right, bottom = min(work[2], rect[2]), min(work[3], rect[3])
    args = [
        ffmpeg(),
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-thread_queue_size",
        "256",
        "-f",
        "gdigrab",
        "-framerate",
        "25",
        "-draw_mouse",
        "1",
        "-offset_x",
        str(left),
        "-offset_y",
        str(top),
        "-video_size",
        f"{right - left}x{bottom - top}",
        "-i",
        "desktop",
        "-i",
        str(audio),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-shortest",
        "-t",
        f"{duration:.3f}",
        "-vf",
        "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        "-r",
        "25",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "21",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-ar",
        "48000",
        "-movflags",
        "+faststart",
        str(destination),
    ]
    return subprocess.Popen(args, stdin=subprocess.PIPE, stdout=log, stderr=log), log
