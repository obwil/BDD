# renommer_videos_desc.py
# Dans les dossiers des activités vides en BDD ayant un _DESC_ vidéo,
# renomme les fichiers vidéo dont le nom commence par _DESC_ en supprimant ce préfixe.
#
# SIMULATION = True  : affiche les renommages prévus sans rien modifier
# SIMULATION = False : effectue les renommages

import sqlite3
from pathlib import Path

# =============================================================================
SIMULATION = False
# =============================================================================

DB_PATH = Path(__file__).parent / "activites.db"
ACTIVITES_DIR = Path(r"C:\Users\moina\Dropbox\Animation\Activités v2")

EXT_VIDEO = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"}

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
vides = conn.execute("""
    SELECT a.id, a.nom FROM activite a
    WHERE (a.description IS NULL OR a.description = '')
    AND NOT EXISTS (SELECT 1 FROM activite_thematique at2 WHERE at2.activite_id = a.id)
    AND NOT EXISTS (SELECT 1 FROM activite_cycle ac WHERE ac.activite_id = a.id)
    ORDER BY a.nom
""").fetchall()
conn.close()

a_renommer = []

for r in vides:
    dossier = ACTIVITES_DIR / r["nom"]
    if not dossier.exists():
        continue
    for f in dossier.iterdir():
        if (f.name.upper().startswith("_DESC_")
                and f.suffix.lower() in EXT_VIDEO):
            nouveau_nom = f.name[len("_DESC_"):]  # retire le préfixe _DESC_
            nouveau_chemin = f.parent / nouveau_nom
            a_renommer.append((r["id"], r["nom"], f, nouveau_chemin))

print(f"MODE : {'SIMULATION' if SIMULATION else 'RÉEL'}")
print(f"Fichiers à renommer : {len(a_renommer)}")
print("-" * 70)

erreurs = 0
for aid, nom, ancien, nouveau in a_renommer:
    print(f"  id={aid:<5} | {nom}")
    print(f"    {ancien.name}  →  {nouveau.name}")
    if not SIMULATION:
        if nouveau.exists():
            print(f"    ⚠️  CONFLIT : {nouveau.name} existe déjà, ignoré")
            erreurs += 1
            continue
        try:
            ancien.rename(nouveau)
            print(f"    ✅ Renommé")
        except Exception as e:
            print(f"    ❌ Erreur : {e}")
            erreurs += 1

print("-" * 70)
if SIMULATION:
    print(f"SIMULATION terminée. {len(a_renommer)} fichiers seraient renommés.")
    print("Mettre SIMULATION = False pour effectuer les renommages.")
else:
    print(f"Terminé. {len(a_renommer) - erreurs}/{len(a_renommer)} fichiers renommés.")

import os
os.system("pause")
