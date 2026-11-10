@echo off
call "%~dp0_run.cmd" codegen
exit /b %errorlevel%
