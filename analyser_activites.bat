@echo off
if "%ANTHROPIC_API_KEY%"=="" (
    echo ERREUR : ANTHROPIC_API_KEY non definie.
    echo Executez : set ANTHROPIC_API_KEY=sk-ant-...
    pause
    exit /b 1
)
pip show anthropic >nul 2>&1 || pip install anthropic python-docx --break-system-packages --quiet
if "%1"=="" (
    python analyser_activites.py
) else (
    python analyser_activites.py --limit %1
)
pause
