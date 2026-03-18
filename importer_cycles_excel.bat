@echo off
chcp 65001 > nul
cd /d "%~dp0"
python importer_cycles_excel.py
pause
