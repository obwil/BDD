@echo off
call "%~dp0_python.bat" || exit /b 1
cd /d "%~dp0"
set "URL=http://localhost:8000/static/taches.html"

:: Si l'application tourne deja (port 8000), on ouvre simplement la page
netstat -ano | findstr /r /c:":8000 .*LISTENING" >nul
if not errorlevel 1 (
    start "" "%URL%"
    exit /b 0
)

"%PYTHON%" -m pip install -r requirements.txt --quiet
start "" cmd /c "timeout /t 3 /nobreak >nul && start "" "%URL%""
"%PYTHON%" -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
