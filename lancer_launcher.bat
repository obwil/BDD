@echo off
call "%~dp0_python.bat" || exit /b 1
cd /d "%~dp0"
"%PYTHON%" -m pip install flask --quiet
start "" "http://localhost:18766"
"%PYTHON%" launcher_server.py
pause
