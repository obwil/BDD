@echo off
call "%~dp0_python.bat" || exit /b 1
cd /d "%~dp0"
"%PYTHON%" -m pip install pyinstaller --quiet
"%PYTHON%" -m PyInstaller --noconfirm --onefile --windowed --name "BDD Launcher" launcher_start.py
"%PYTHON%" -m PyInstaller --noconfirm --onefile --windowed --name "BDD Demarrage" demarrage_start.py
echo.
echo Les fichiers executables sont dans le dossier dist\
echo  - BDD Demarrage.exe : demarre l'application + l'avancement du travail
echo  - BDD Launcher.exe  : tous les outils
echo Vous pouvez les epingler a la barre des taches.
pause
