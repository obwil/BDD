# =============================================================================
# reinitialiser_associations.py
# =============================================================================
# Supprime uniquement les associations activite_attendu et activite_cycle.
# Comportement sur activite_cycle_analysee selon REINITIALISER_CYCLES :
#   False (defaut) : preserve les entrees 'inadapte' (issues de importer_cycles_excel)
#                    supprime uniquement les entrees 'ok', 'erreur_parsing', 'prohibited'
#                    -> relancer analyser_attendus_v2.bat directement
#   True           : supprime toutes les entrees (reinitialisation complete)
#                    -> relancer importer_cycles_excel.bat puis analyser_attendus_v2.bat
# Ne touche PAS aux attendus en base (attendu_scolaire).
# SIMULATION = True par defaut.
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

SIMULATION = True
REINITIALISER_CYCLES = False  # True = supprime aussi les entrees 'inadapte'


def main():
    print("=" * 60)
    print("REINITIALISATION DES ASSOCIATIONS")
    print("=" * 60)
    print(f"MODE : {'SIMULATION' if SIMULATION else 'ECRITURE EN BASE'}")
    print(f"REINITIALISER_CYCLES : {REINITIALISER_CYCLES}")
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
    n_inadapte = 0
    if "activite_cycle_analysee" in tables:
        n_suivi = conn.execute(
            "SELECT COUNT(*) FROM activite_cycle_analysee"
        ).fetchone()[0]
        n_inadapte = conn.execute(
            "SELECT COUNT(*) FROM activite_cycle_analysee WHERE statut = 'inadapte'"
        ).fetchone()[0]

    print(f"  {n_liens} associations activite_attendu")
    print(f"  {n_cycles} associations activite_cycle")
    print(f"  {n_suivi} entrees activite_cycle_analysee (dont {n_inadapte} 'inadapte')")
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
        if REINITIALISER_CYCLES:
            conn.execute("DELETE FROM activite_cycle_analysee")
            print(f"  OK : {n_suivi} entrees activite_cycle_analysee supprimees")
        else:
            conn.execute(
                "DELETE FROM activite_cycle_analysee WHERE statut != 'inadapte'"
            )
            n_suppr = n_suivi - n_inadapte
            print(f"  OK : {n_suppr} entrees supprimees ({n_inadapte} 'inadapte' preservees)")

    conn.commit()

    print(f"  OK : {n_liens} liens activite_attendu supprimes")
    print(f"  OK : {n_cycles} liens activite_cycle supprimes")
    print(f"  Les {n_attendus} attendus en base sont intacts.")
    print()

    if REINITIALISER_CYCLES:
        print("  RAPPEL : relancer importer_cycles_excel.bat avant analyser_attendus_v2.bat")
    else:
        print("Vous pouvez relancer analyser_attendus_v2.bat directement.")

    conn.close()


if __name__ == "__main__":
    main()
