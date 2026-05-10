# =============================================================================
# migration_ajout_statut_cycle.py
# =============================================================================
# Ajoute la colonne `statut` a la table activite_cycle_analysee.
# Valeurs possibles : 'ok' | 'erreur_parsing' | 'prohibited'
# Les lignes existantes sont mises a jour avec statut='ok' par defaut.
# =============================================================================

import sqlite3
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

SIMULATION = False  # Mettre False pour appliquer

def main():
    if not DB_PATH.exists():
        print(f"ERREUR : Base SQLite introuvable : {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)

    # Verifier si la colonne existe deja
    cols = [r[1] for r in conn.execute("PRAGMA table_info(activite_cycle_analysee)").fetchall()]
    if "statut" in cols:
        print("INFO : colonne 'statut' deja presente, rien a faire.")
        conn.close()
        return

    print("Colonne 'statut' absente -> migration necessaire.")
    print(f"Mode : {'SIMULATION' if SIMULATION else 'ECRITURE'}")

    if not SIMULATION:
        conn.execute("ALTER TABLE activite_cycle_analysee ADD COLUMN statut TEXT NOT NULL DEFAULT 'ok'")
        conn.commit()
        n = conn.execute("SELECT COUNT(*) FROM activite_cycle_analysee").fetchone()[0]
        print(f"OK : colonne ajoutee, {n} ligne(s) existante(s) mises a 'ok'.")
    else:
        print("SIMULATION : ALTER TABLE activite_cycle_analysee ADD COLUMN statut TEXT NOT NULL DEFAULT 'ok'")
        print("Relancez avec SIMULATION = False pour appliquer.")

    conn.close()

if __name__ == "__main__":
    main()
