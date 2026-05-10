import sqlite3
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path("C:/Users/moina/Dropbox/Outils/BDD activit\u00e9s/_OUTIL/activites.db")
DROPBOX = Path("C:/Users/moina/Dropbox/Animation/Activit\u00e9s v2")
OUTPUT = Path("C:/Users/moina/Dropbox/Outils/BDD activit\u00e9s/_OUTIL/nouvelles_activites.txt")

try:
    conn = sqlite3.connect(str(DB_PATH))
    noms_bdd = {r[0] for r in conn.execute("SELECT nom FROM activite").fetchall()}
    conn.close()

    nouvelles = []
    for d in DROPBOX.iterdir():
        if d.is_dir() and not d.name.startswith("_"):
            if d.name not in noms_bdd:
                nouvelles.append(d.name)

    lines = [f"Nouvelles activites : {len(nouvelles)}"]
    for n in sorted(nouvelles):
        lines.append(f" - {n}")

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK - {len(nouvelles)} nouvelles activites -> {OUTPUT}")
except Exception as e:
    OUTPUT.write_text(f"ERREUR: {e}", encoding="utf-8")
    print(f"ERREUR: {e}")
