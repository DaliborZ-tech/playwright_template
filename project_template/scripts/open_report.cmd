@echo off
setlocal
cd /d "%~dp0.."
if not exist "reports\report.html" (
  echo Report zatim neexistuje. Nejprve spustte scripts\run_tests.cmd.
  exit /b 2
)
start "" "reports\report.html"
