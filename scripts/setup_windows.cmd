@echo off
setlocal
set PYTHONUTF8=1
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" goto existing
where py >nul 2>nul
if errorlevel 1 goto fallback
py -3.12 -c "import sys; raise SystemExit(sys.version_info[:2] != (3,12))" >nul 2>nul
if not "%errorlevel%"=="0" goto astral
py -3.12 scripts\bootstrap.py
exit /b %errorlevel%
:astral
py -V:Astral/CPython3.12 -c "import sys; raise SystemExit(sys.version_info[:2] != (3,12))" >nul 2>nul
if not "%errorlevel%"=="0" goto fallback
py -V:Astral/CPython3.12 scripts\bootstrap.py
exit /b %errorlevel%
:fallback
where python >nul 2>nul
if errorlevel 1 (
  echo Python neni dostupny. Nainstalujte Python 3.12 z https://www.python.org/downloads/
  exit /b 2
)
python scripts\bootstrap.py
exit /b %errorlevel%
:existing
".venv\Scripts\python.exe" scripts\bootstrap.py
exit /b %errorlevel%

