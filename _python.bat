@echo off
rem Trouve l'interpreteur Python installe sur CE poste et le met dans la variable PYTHON.
rem Utilisation dans un autre .bat :
rem     call "%~dp0_python.bat" || exit /b 1
rem     "%PYTHON%" mon_script.py
set "PYTHON="

rem 1) Lanceur officiel "py" (installe avec Python depuis python.org)
for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON=%%P"
if defined PYTHON exit /b 0

rem 2) Installation "utilisateur" classique
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do if exist "%%D\python.exe" set "PYTHON=%%D\python.exe"
if defined PYTHON exit /b 0

rem 3) "python" dans le PATH
for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON=%%P"
if defined PYTHON exit /b 0

echo ERREUR : Python introuvable sur ce poste (%COMPUTERNAME%).
echo Installez Python depuis https://www.python.org puis relancez.
pause
exit /b 1
