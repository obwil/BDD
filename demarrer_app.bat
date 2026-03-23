@echo off
if not exist "activites.db" (
    echo ERREUR : activites.db introuvable. Lancez d'abord les scripts d'import.
    pause
    exit /b 1
)
if not exist "static" mkdir static
if not exist "static\index.html" (
    if exist "index.html" copy "index.html" "static\index.html" > nul
)
pip install fastapi uvicorn[standard] --break-system-packages --quiet
start "" "http://localhost:8000"
start "" "http://localhost:8000/static/dashboard_bdd.html"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
