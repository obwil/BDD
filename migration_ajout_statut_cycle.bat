@echo off
chcp 65001 > nul
cd /d "%~dp0"
python migration_ajout_statut_cycle.py
pause
