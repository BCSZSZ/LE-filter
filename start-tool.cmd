@echo off
cd /d "%~dp0"
py -3 -X utf8 tool\server.py --open
pause
