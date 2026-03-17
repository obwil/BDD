# =============================================================================
# reinitialiser_associations.py
# =============================================================================
# Supprime uniquement les associations activite_attendu, activite_cycle
# et activite_cycle_analysee.
# Ne touche PAS aux attendus en base (attendu_scolaire).
# Utile pour relancer une analyse depuis zero sans reimporter les attendus.
# SIMULATION = True par defaut.
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

SIMULATION = True


def main():
    print("=" * 60)
    print("REINITIALISATION DES ASSOCIATIONS")
    print("=" * 60)
    print(f"MODE : {'SIMULATION' if SIMULATION else 'ECRITURE EN BASE'}")
    print()

    if not DB_PATH.exists():
        print(f"ERREUR : Base introuvable : {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)

    n_liens    = conn.execute("SELECT COUNT(*) FROM activite_attendu").fetchone()[0]
    n_cycles   = conn.execute("SELECT COUNT(*) FROM activite_cycle").fetchone()[0]
    n_attendus = conn.execute("SELECT COUNT(*) FROM attendu_scolaire").fetchone()[0]

    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()]
    n_suivi = 0
    if "activite_cycle_analysee" in tables:
        n_suivi = conn.execute(
            "SELECT COUNT(*) FROM activite_cycle_analysee"
        ).fetchone()[0]

    print(f"  {n_liens} associations activite_attendu")
    print(f"  {n_cycles} associations activite_cycle")
    print(f"  {n_suivi} entrees activite_cycle_analysee")
    print(f"  {n_attendus} attendus en base (non touches)")
    print()

    if SIMULATION:
        print(">>> Simulation : aucune donnee modifiee.")
        print("    Mettre SIMULATION = False pour appliquer.")
        conn.close()
        return

    import shutil
    backup = DB_PATH.parent / "activites.db.backup"
    shutil.copy2(DB_PATH, backup)
    print(f"  Sauvegarde : {backup}")

    conn.execute("DELETE FROM activite_attendu")
    conn.execute("DELETE FROM activite_cycle")
    if "activite_cycle_analysee" in tables:
        conn.execute("DELETE FROM activite_cycle_analysee")
    conn.commit()

    print(f"  OK : {n_liens} liens activite_attendu supprimes")
    print(f"  OK : {n_cycles} liens activite_cycle supprimes")
    print(f"  OK : {n_suivi} entrees activite_cycle_analysee supprimees")
    print(f"  Les {n_attendus} attendus en base sont intacts.")
    print()
    print("Vous pouvez relancer analyser_attendus_v2.bat directement.")

    conn.close()


if __name__ == "__main__":
    main()
