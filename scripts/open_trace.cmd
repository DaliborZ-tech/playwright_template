@echo off
call "%~dp0_run.cmd" trace %*
exit /b %errorlevel%
