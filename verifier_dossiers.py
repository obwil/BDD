# verifier_dossiers.py
# Verifie quelles activites de la BDD n'ont pas de dossier existant sur le disque.

import sqlite3
from pathlib import Path
from urllib.parse import unquote

DB_PATH = Path(__file__).parent / "activites.db"
DROPBOX_ACTIVITES = Path(r"C:\Users\moina\Dropbox\Animation\Activités v2")

def nom_dossier(chemin):
    if not chemin:
        return ""
    if chemin.startswith("file:///"):
        chemin = unquote(chemin[8:])
    return chemin.replace("/", "\\").split("\\")[-1]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT id, nom, chemin_dossier FROM activite ORDER BY nom").fetchall()
conn.close()

dossiers_disque = {d.name for d in DROPBOX_ACTIVITES.iterdir() if d.is_dir()}

manquants = []
for r in rows:
    dnom = nom_dossier(r["chemin_dossier"])
    if dnom not in dossiers_disque:
        manquants.append((r["id"], r["nom"], dnom))

print(f"Total activites en BDD      : {len(rows)}")
print(f"Total dossiers sur disque   : {len(dossiers_disque)}")
print(f"Activites sans dossier      : {len(manquants)}")

if manquants:
    print()
    print("-" * 70)
    for aid, nom, dnom in manquants:
        print(f"  id={aid:<5} | nom BDD         : {nom}")
        if dnom != nom:
            print(f"         | dossier attendu : {dnom}")
    print("-" * 70)
else:
    print("\nOK - Tous les dossiers existent sur le disque.")

import os
os.system("pause")
