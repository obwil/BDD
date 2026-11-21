@echo off
call "%~dp0_python.bat" || exit /b 1
title Serveur dossiers generiques
start "" "http://localhost:18765"
"%PYTHON%" "%~dp0open_server.py"
pause
