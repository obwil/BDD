# =============================================================================
# reinitialiser_attendus_v2.py
# =============================================================================
# Supprime TOUTES les associations activite_attendu, activite_cycle,
# activite_cycle_analysee, puis vide entierement attendu_scolaire.
# A executer avant import_attendus_v2.py lors d'une refonte complete.
# SIMULATION = True par defaut.
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

SIMULATION = True


def main():
    print("=" * 60)
    print("REINITIALISATION COMPLETE DES ATTENDUS")
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

    # Table de suivi v2 (peut ne pas exister encore)
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
    print(f"  {n_attendus} attendus en base")
    print()

    if SIMULATION:
        print(">>> Simulation : aucune donnee modifiee.")
        print("    Mettre SIMULATION = False pour appliquer.")
        conn.close()
        return

    # Sauvegarde automatique
    import shutil
    backup = DB_PATH.parent / "activites.db.backup"
    shutil.copy2(DB_PATH, backup)
    print(f"  Sauvegarde : {backup}")

    conn.execute("DELETE FROM activite_attendu")
    conn.execute("DELETE FROM activite_cycle")
    if "activite_cycle_analysee" in tables:
        conn.execute("DELETE FROM activite_cycle_analysee")
    # Table de suivi ancienne (compatibilite)
    if "activite_disc_analysee" in tables:
        conn.execute("DELETE FROM activite_disc_analysee")
    conn.execute("DELETE FROM attendu_scolaire")
    conn.commit()

    print(f"  OK : {n_liens} liens supprimes, {n_attendus} attendus supprimes.")
    print()
    print("Relancez maintenant dans l'ordre :")
    print("  1. migration_ajout_suivi_cycle.bat")
    print("  2. import_attendus_v2.bat")
    conn.close()


if __name__ == "__main__":
    main()
