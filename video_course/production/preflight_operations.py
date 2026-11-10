"""Skutečné ověření terminálu, selhání, Trace Vieweru a Inspectoru před dlouhým záznamem."""

import json
import subprocess
from pathlib import Path

from record_course import ROOT, WORKSPACE, ensure_demo, ensure_sources, read_json
from studio import Studio, focus, wait_until


def snapshot(handle, destination):
    import win32api
    import win32gui
    from PIL import ImageGrab

    focus(handle)
    rect = win32gui.GetWindowRect(handle)
    work = win32api.GetMonitorInfo(win32api.MonitorFromWindow(handle))["Work"]
    box = (
        max(work[0], rect[0]),
        max(work[1], rect[1]),
        min(work[2], rect[2]),
        min(work[3], rect[3]),
    )
    ImageGrab.grab(bbox=box).save(destination)


def main():
    ensure_sources()
    demo = ensure_demo()
    subprocess.run(
        [
            str(ROOT / ".venv/Scripts/python.exe"),
            str(Path(__file__).with_name("open_studio.py")),
            "--workspace",
            str(WORKSPACE),
        ],
        check=True,
    )
    studio = Studio()
    result = {}
    try:
        _, run = studio.terminal("failure", "preflight_failure")
        run()
        path = WORKSPACE / "reports/terminal_preflight_failure.json"
        wait_until(lambda: read_json(path).get("exit_code") != 777, timeout=45)
        result["failure"] = read_json(path)
        if result["failure"]["exit_code"] != 1:
            raise RuntimeError("Výukový test neselhal očekávaným assertionem.")
        frame_folder = ROOT / "evidence/video-frames"
        snapshot(studio.editor, frame_folder / "real-terminal-failure.png")
        handle, show = studio.trace()
        show()
        snapshot(handle, frame_folder / "real-trace-viewer.png")
        result["trace_viewer"] = "opened_actual_failure_trace"
        handle, step = studio.debug()
        step()
        snapshot(handle, frame_folder / "real-inspector.png")
        result["inspector"] = "opened_and_stepped_actual_pytest"
        (ROOT / "evidence/production-operations-preflight.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(result), flush=True)
    finally:
        studio.close()
        if demo and demo.poll() is None:
            demo.terminate()


if __name__ == "__main__":
    main()
