@echo off
setlocal
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
  echo Chybi prostredi .venv. Nejprve spustte scripts\setup_windows.cmd
  exit /b 2
)
set PYTHONUTF8=1
".venv\Scripts\python.exe" scripts\manage.py %*
exit /b %errorlevel%

