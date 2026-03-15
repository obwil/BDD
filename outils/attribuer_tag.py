# =============================================================================
# attribuer_tag.py
# =============================================================================
# Cree un tag et l'attribue aux activites dont le nom est liste dans un
# fichier .txt (un nom par ligne).
#
# CONFIGURATION : modifier les deux variables ci-dessous, puis lancer.
# =============================================================================

import sqlite3
from pathlib import Path

# DB a la racine de _OUTIL, un niveau au-dessus de outil/
DB_PATH = Path(__file__).parent.parent / "activites.db"

# --- A MODIFIER ---
NOM_TAG = "Incarner le vivant"
FICHIER_NOMS = Path(__file__).parent / "tags" / "incarner_le_vivant.txt"
# ------------------

# Mettre False pour ecrire reellement en base
SIMULATION = False

# =============================================================================

def main():
    if not DB_PATH.exists():
        print(f"ERREUR : Base introuvable : {DB_PATH}")
        return

    if not FICHIER_NOMS.exists():
        print(f"ERREUR : Fichier introuvable : {FICHIER_NOMS}")
        return

    noms_cibles = set()
    for ligne in FICHIER_NOMS.read_text(encoding="utf-8").splitlines():
        nom = ligne.strip()
        if nom:
            noms_cibles.add(nom)

    print("=" * 60)
    print(f"TAG         : {NOM_TAG}")
    print(f"FICHIER     : {FICHIER_NOMS.name}")
    print(f"NOMS LUS    : {len(noms_cibles)}")
    print(f"MODE        : {'SIMULATION' if SIMULATION else 'ECRITURE EN BASE'}")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    toutes = conn.execute("SELECT id, nom FROM activite").fetchall()
    noms_cibles_lower = {n.lower(): n for n in noms_cibles}

    trouves = []
    non_trouves = []

    for a in toutes:
        if a["nom"].lower() in noms_cibles_lower:
            trouves.append(a)

    noms_trouves_lower = {a["nom"].lower() for a in trouves}
    for nom in noms_cibles:
        if nom.lower() not in noms_trouves_lower:
            non_trouves.append(nom)

    print(f"\nActivites trouvees en base : {len(trouves)}")
    for a in trouves:
        print(f"  [OK] {a['nom']}")

    if non_trouves:
        print(f"\nActivites NON trouvees en base ({len(non_trouves)}) :")
        for nom in sorted(non_trouves):
            print(f"  [??] {nom}")

    if SIMULATION:
        print(f"\n>>> Simulation : {len(trouves)} attribution(s) seraient creees pour le tag '{NOM_TAG}'.")
        print("    Mettre SIMULATION = False pour appliquer.")
        conn.close()
        return

    if not trouves:
        print("\nAucune activite a traiter.")
        conn.close()
        return

    existing = conn.execute("SELECT id FROM tag WHERE nom = ?", (NOM_TAG,)).fetchone()
    if existing:
        tag_id = existing["id"]
        print(f"\nTag '{NOM_TAG}' existant (id={tag_id})")
    else:
        cur = conn.execute("INSERT INTO tag (nom) VALUES (?)", (NOM_TAG,))
        tag_id = cur.lastrowid
        print(f"\nTag '{NOM_TAG}' cree (id={tag_id})")

    ok = 0
    for a in trouves:
        conn.execute(
            "INSERT OR IGNORE INTO activite_tag (activite_id, tag_id) VALUES (?, ?)",
            (a["id"], tag_id)
        )
        ok += 1

    conn.commit()
    conn.close()

    print(f"{ok} attribution(s) enregistree(s).")
    print("Termine.")


if __name__ == "__main__":
    main()
