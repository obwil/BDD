@echo off
cd /d "%~dp0"
"C:\Users\moina\AppData\Local\Programs\Python\Python313\python.exe" -m pip install pyinstaller --quiet
"C:\Users\moina\AppData\Local\Programs\Python\Python313\python.exe" -m PyInstaller --onefile --windowed --name "BDD Launcher" launcher_start.py
echo.
echo Le fichier executable est dans le dossier dist\
echo Vous pouvez l'epingler a la barre des taches.
pause
