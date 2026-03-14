@echo off
python migrate_excel.py > migration_log.txt 2>&1
echo Termine. Ouvrez migration_log.txt pour voir le resultat.
pause
