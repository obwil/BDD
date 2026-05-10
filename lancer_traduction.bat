@echo off
cd /d "%~dp0"

"C:\Users\moina\AppData\Local\Programs\Python\Python313\python.exe" -m pip install langdetect pdfplumber python-docx pytesseract pillow google-genai --quiet

"C:\Users\moina\AppData\Local\Programs\Python\Python313\python.exe" traduire_desc_anglais.py
pause
