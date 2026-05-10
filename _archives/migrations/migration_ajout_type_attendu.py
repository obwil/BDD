# =============================================================================
# migration_ajout_type_attendu.py
# =============================================================================
# Ajoute la colonne `type` a la table attendu_scolaire.
# Met tous les attendus existants a 'EDD' par defaut.
# Idempotent : verifie si la colonne existe avant d'agir.
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"


def main():
    print("=" * 60)
    print("MIGRATION : ajout colonne type a attendu_scolaire")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERREUR : Base SQLite introuvable : {DB_PATH}")
        print("   Lancez d'abord create_schema.py")
        return

    conn = sqlite3.connect(DB_PATH)

    cols = [row[1] for row in conn.execute("PRAGMA table_info(attendu_scolaire)").fetchall()]

    if "type" in cols:
        print("OK : colonne 'type' deja presente. Rien a faire.")
        conn.close()
        return

    conn.execute("ALTER TABLE attendu_scolaire ADD COLUMN type TEXT NOT NULL DEFAULT 'EDD'")
    conn.commit()

    n = conn.execute("SELECT COUNT(*) FROM attendu_scolaire").fetchone()[0]
    print(f"OK : colonne 'type' ajoutee. {n} attendus existants marques 'EDD'.")

    conn.close()
    print("Migration terminee.")


if __name__ == "__main__":
    main()
