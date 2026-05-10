# =============================================================================
# migration_ajout_suivi_cycle.py
# =============================================================================
# Cree la table activite_cycle_analysee si elle est absente.
# Remplace activite_disc_analysee : suit la progression par cycle.
# Idempotent.
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"


def main():
    print("=" * 60)
    print("MIGRATION : table activite_cycle_analysee")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERREUR : Base introuvable : {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS activite_cycle_analysee (
            activite_id  INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
            cycle_id     INTEGER NOT NULL REFERENCES cycle(id) ON DELETE CASCADE,
            PRIMARY KEY (activite_id, cycle_id)
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_aca_cycle ON activite_cycle_analysee(cycle_id)"
    )
    conn.commit()

    n = conn.execute(
        "SELECT COUNT(*) FROM activite_cycle_analysee"
    ).fetchone()[0]
    print(f"OK : table activite_cycle_analysee prete ({n} entrees).")
    conn.close()


if __name__ == "__main__":
    main()
