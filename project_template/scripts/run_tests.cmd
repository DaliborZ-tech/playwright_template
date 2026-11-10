@echo off
setlocal
set PYTHONUTF8=1
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
  echo Nejprve spustte scripts\setup_windows.cmd.
  exit /b 2
)
".venv\Scripts\python.exe" -m pytest %*
exit /b %errorlevel%
