@echo off
cd /d "%~dp0"
"C:\Users\moina\AppData\Local\Programs\Python\Python313\python.exe" -m pip install flask --quiet
start "" "http://localhost:18766"
"C:\Users\moina\AppData\Local\Programs\Python\Python313\python.exe" launcher_server.py
pause
