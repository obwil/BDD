@echo off
call "%~dp0_python.bat" || exit /b 1
cd /d "%~dp0"

"%PYTHON%" -m pip install langdetect pdfplumber python-docx pytesseract pillow google-genai --quiet

"%PYTHON%" traduire_desc_anglais.py
pause
