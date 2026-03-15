# =============================================================================
# renommer_tag.py
# =============================================================================
# Renomme un tag existant en base.
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "activites.db"

# --- A MODIFIER ---
NOM_ACTUEL = "Conte"
NOUVEAU_NOM = "Histoire - Conte"
# ------------------

def main():
    if not DB_PATH.exists():
        print(f"ERREUR : Base introuvable : {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    tag = conn.execute("SELECT id, nom FROM tag WHERE nom = ?", (NOM_ACTUEL,)).fetchone()

    if not tag:
        print(f"ERREUR : Tag '{NOM_ACTUEL}' introuvable en base.")
        print()
        print("Tags existants :")
        for t in conn.execute("SELECT id, nom FROM tag ORDER BY nom").fetchall():
            print(f"  [{t['id']}] {t['nom']}")
        conn.close()
        return

    conflit = conn.execute("SELECT id FROM tag WHERE nom = ?", (NOUVEAU_NOM,)).fetchone()
    if conflit:
        print(f"ERREUR : Un tag '{NOUVEAU_NOM}' existe déjà (id={conflit['id']}).")
        conn.close()
        return

    conn.execute("UPDATE tag SET nom = ? WHERE id = ?", (NOUVEAU_NOM, tag["id"]))
    conn.commit()
    conn.close()

    print(f"Tag renommé : '{NOM_ACTUEL}' -> '{NOUVEAU_NOM}'")

if __name__ == "__main__":
    main()
