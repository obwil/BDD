@echo off
if "%GEMINI_API_KEY%"=="" (
    echo ERREUR : GEMINI_API_KEY non definie.
    echo Executez : setx GEMINI_API_KEY "votre-cle"
    pause
    exit /b 1
)
pip show google-generativeai >nul 2>&1 || pip install google-generativeai python-docx --break-system-packages --quiet
python analyser_attendus_disciplinaires.py
pause
