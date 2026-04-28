# checker_desc_mixtes.py
# Identifie les activités vides en BDD dont le dossier contient
# à la fois un _DESC_ vidéo ET un _DESC_ dans un autre format.

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"
ACTIVITES_DIR = Path(r"C:\Users\moina\Dropbox\Animation\Activités v2")

EXT_VIDEO = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"}
EXT_TEXTE = {".txt", ".pdf", ".docx", ".html", ".md"}
EXT_IMAGE = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".jfif"}

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

mixtes = []
video_seul = []

for r in vides:
    dossier = ACTIVITES_DIR / r["nom"]
    if not dossier.exists():
        continue
    desc_files = [f for f in dossier.iterdir() if "_DESC_" in f.name.upper()]
    if not desc_files:
        continue

    a_video  = any(f.suffix.lower() in EXT_VIDEO for f in desc_files)
    a_texte  = any(f.suffix.lower() in EXT_TEXTE for f in desc_files)
    a_image  = any(f.suffix.lower() in EXT_IMAGE for f in desc_files)
    a_autre  = any(f.suffix.lower() not in EXT_VIDEO | EXT_TEXTE | EXT_IMAGE for f in desc_files)

    if a_video:
        if a_texte or a_image or a_autre:
            mixtes.append((r["id"], r["nom"], desc_files))
        else:
            video_seul.append((r["id"], r["nom"], desc_files))

print(f"Activités avec _DESC_ vidéo UNIQUEMENT    : {len(video_seul)}")
print(f"Activités avec _DESC_ vidéo + autre format : {len(mixtes)}")

if mixtes:
    print("\n--- MIXTES (vidéo + autre) ---")
    for aid, nom, fichiers in mixtes:
        print(f"\n  id={aid} | {nom}")
        for f in fichiers:
            ext = f.suffix.lower()
            cat = "VIDEO" if ext in EXT_VIDEO else "TEXTE" if ext in EXT_TEXTE else "IMAGE" if ext in EXT_IMAGE else "AUTRE"
            print(f"    [{cat}] {f.name}")

if video_seul:
    print("\n--- VIDÉO SEUL ---")
    for aid, nom, fichiers in video_seul:
        print(f"\n  id={aid} | {nom}")
        for f in fichiers:
            print(f"    {f.name}")

import os
os.system("pause")
