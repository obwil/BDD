# scanner_desc_types.py
# Scanne les dossiers des activités vides et identifie le type de _DESC_

import sqlite3
from pathlib import Path
from urllib.parse import unquote

DB_PATH = Path(__file__).parent / "activites.db"
ACTIVITES_DIR = Path(r"C:\Users\moina\Dropbox\Animation\Activités v2")

EXT_VIDEO  = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"}
EXT_TEXTE  = {".txt", ".pdf", ".docx", ".html", ".md"}
EXT_IMAGE  = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".jfif"}

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

categories = {"video": [], "texte": [], "image": [], "autre": [], "aucun": [], "dossier_absent": []}

for r in vides:
    dossier = ACTIVITES_DIR / r["nom"]
    if not dossier.exists():
        categories["dossier_absent"].append((r["id"], r["nom"], []))
        continue

    desc_files = [f for f in dossier.iterdir() if "_DESC_" in f.name.upper()]
    if not desc_files:
        categories["aucun"].append((r["id"], r["nom"], []))
        continue

    extensions = {f.suffix.lower() for f in desc_files}
    noms = [f.name for f in desc_files]

    if extensions & EXT_VIDEO:
        categories["video"].append((r["id"], r["nom"], noms))
    elif extensions & EXT_TEXTE:
        categories["texte"].append((r["id"], r["nom"], noms))
    elif extensions & EXT_IMAGE:
        categories["image"].append((r["id"], r["nom"], noms))
    else:
        categories["autre"].append((r["id"], r["nom"], noms))

print("=" * 70)
for cat, items in categories.items():
    print(f"\n[{cat.upper()}] ({len(items)} activités)")
    print("-" * 70)
    for aid, nom, fichiers in items:
        print(f"  id={aid:<5} | {nom}")
        for f in fichiers:
            print(f"            └── {f}")

print("\n" + "=" * 70)
print("RÉSUMÉ :")
for cat, items in categories.items():
    print(f"  {cat:<20} : {len(items)}")

import os
os.system("pause")
