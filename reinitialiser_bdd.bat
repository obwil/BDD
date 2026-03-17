@echo off
echo Reinitialisation de la base de donnees...
echo.
echo ATTENTION : toutes les donnees seront effacees.
pause

if exist "activites.db" del "activites.db"
echo Base supprimee.

python create_schema.py
python migrate_excel.py
python import_classification.py
python import_pedagogies.py
python import_attendus.py
python migration_ajout_cycle.py
python migration_ajout_type_attendu.py
python import_attendus_disciplinaires.py

echo.
echo Reinitialisation terminee.
pause
