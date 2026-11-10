"""Ověří generátor a skutečný GREEN/RED běh šablony proti lokálnímu HTTP serveru."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import venv
import xml.etree.ElementTree as ET
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from new_project import FILES

ROOT = Path(__file__).resolve().parents[1]


def run(command, cwd, environment):
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


class Handler(BaseHTTPRequestHandler):
    failure = False

    def do_GET(self):
        body = b"<!doctype html><html><body><h1>Template verification</h1></body></html>"
        self.send_response(503 if self.failure else 200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


def main():
    parent = ROOT / ".tools/template-verification"
    parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="New project check ", dir=parent))
    project = work / "My test project"
    generator = ROOT / "scripts/new_project.py"
    environment = {**os.environ, "PYTHONUTF8": "1"}
    environment.pop("BASE_URL", None)
    created = run(
        [sys.executable, str(generator), str(project), "--name", "Customer Tests", "--git"],
        ROOT,
        environment,
    )
    assert created.returncode == 0, created.stderr
    assert {
        p.relative_to(project).as_posix()
        for p in project.rglob("*")
        if p.is_file() and ".git" not in p.relative_to(project).parts
    } == set(FILES)
    assert 'name = "customer-tests"' in (project / "pyproject.toml").read_text(encoding="utf-8")
    readme_sha = hashlib.sha256((project / "README.md").read_bytes()).hexdigest()
    refused = run([sys.executable, str(generator), str(project)], ROOT, environment)
    assert refused.returncode == 2
    assert hashlib.sha256((project / "README.md").read_bytes()).hexdigest() == readme_sha

    archive_path = work / "template.zip"
    archived = run(
        [sys.executable, str(generator), "--archive", str(archive_path)], ROOT, environment
    )
    assert archived.returncode == 0, archived.stderr
    with zipfile.ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == set(FILES)

    # Use the already verified pinned dependencies through a .pth file.
    # This checks real launchers and browser runs, not a fresh network install.
    venv.EnvBuilder(with_pip=False).create(project / ".venv")
    site = project / ".venv/Lib/site-packages"
    (site / "verified_dependencies.pth").write_text(
        str(Path(sys.prefix) / "Lib/site-packages") + "\n", encoding="utf-8"
    )
    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}"
        (project / ".env").write_text(f"BASE_URL={url}\n", encoding="utf-8")
        command = ["cmd.exe", "/d", "/c", r"scripts\run_tests.cmd", "-m", "smoke"]
        try:
            green = run(command, project, environment)
            (work / "green.log").write_text(green.stdout + green.stderr, encoding="utf-8")
            assert green.returncode == 0, green.stdout + green.stderr
            junit = ET.parse(project / "reports/junit.xml")
            assert len(junit.findall(".//testcase")) == 1
            assert not junit.findall(".//failure") and not junit.findall(".//error")
            (work / "green.junit.xml").write_bytes((project / "reports/junit.xml").read_bytes())
            assert (project / "reports/report.html").is_file()

            Handler.failure = True
            red_env = {**environment, "BASE_URL": "http://127.0.0.1:1"}
            red = run([*command, "--base-url", url], project, red_env)
            (work / "red.log").write_text(red.stdout + red.stderr, encoding="utf-8")
            assert red.returncode == 1, red.stdout + red.stderr
            assert "HTTP 503" in red.stdout
            junit = ET.parse(project / "reports/junit.xml")
            assert len(junit.findall(".//failure")) == 1 and not junit.findall(".//error")
            assert list((project / "reports/artifacts").rglob("trace.zip"))
            assert list((project / "reports/artifacts").rglob("*.png"))
            assert list((project / "reports/artifacts").rglob("*.webm"))
        finally:
            server.shutdown()
            thread.join(timeout=5)

    status = run(["git", "ls-files", "--others", "--exclude-standard", "-z"], project, environment)
    assert status.returncode == 0
    candidates = {name for name in status.stdout.split("\0") if name}
    assert candidates == set(FILES), candidates.symmetric_difference(FILES)
    report = {
        "result": "PASS",
        "generated_files": len(FILES),
        "destination_with_spaces": True,
        "new_independent_git": True,
        "nonempty_destination_refused_without_changes": True,
        "archive_exact_safe_file_list": True,
        "green_testcases": 1,
        "red_expected_failures": 1,
        "windows_launcher_exit_codes": [green.returncode, red.returncode],
        "dotenv_and_cli_override_verified": True,
        "html_junit_trace_screenshot_video": True,
        "git_excludes_env_venv_reports": True,
        "environment": "New venv reuses existing pinned dependencies; not a fresh pip install",
        "evidence": str(work.relative_to(ROOT)),
    }
    (parent / "validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
