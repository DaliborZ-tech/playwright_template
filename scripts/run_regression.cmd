@echo off
call "%~dp0_run.cmd" regression
exit /b %errorlevel%
