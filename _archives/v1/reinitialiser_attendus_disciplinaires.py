# =============================================================================
# reinitialiser_attendus_disciplinaires.py
# =============================================================================
# Supprime UNIQUEMENT les associations activite_attendu liees aux attendus
# disciplinaires. Ne touche pas aux attendus EDD ni aux autres donnees.
#
# Utile apres un test insatisfaisant (LIMITE = 5) pour repartir proprement
# avant de relancer analyser_attendus_disciplinaires.py.
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

# Mettre False pour executer reellement
SIMULATION = False


def main():
    print("=" * 60)
    print("REINITIALISATION ASSOCIATIONS ATTENDUS DISCIPLINAIRES")
    print("=" * 60)
    print(f"MODE : {'SIMULATION' if SIMULATION else 'ECRITURE EN BASE'}")
    print()

    if not DB_PATH.exists():
        print(f"ERREUR : Base introuvable : {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)

    # Verifier que la colonne type existe
    cols = [row[1] for row in conn.execute("PRAGMA table_info(attendu_scolaire)").fetchall()]
    if "type" not in cols:
        print("ERREUR : colonne 'type' absente. Rien a faire.")
        conn.close()
        return

    # Compter ce qui va etre supprime
    n_liens = conn.execute("""
        SELECT COUNT(*) FROM activite_attendu aa
        JOIN attendu_scolaire a ON a.id = aa.attendu_id
        WHERE a.type = 'disciplinaire'
    """).fetchone()[0]

    n_activites = conn.execute("""
        SELECT COUNT(DISTINCT aa.activite_id) FROM activite_attendu aa
        JOIN attendu_scolaire a ON a.id = aa.attendu_id
        WHERE a.type = 'disciplinaire'
    """).fetchone()[0]

    print(f"  Associations disciplinaires en base : {n_liens} liens sur {n_activites} activite(s)")
    print()

    if n_liens == 0:
        print("Aucune association disciplinaire a supprimer.")
        conn.close()
        return

    if SIMULATION:
        print(f">>> Simulation : {n_liens} lien(s) seraient supprimes sur {n_activites} activite(s).")
        print("    Mettre SIMULATION = False pour appliquer.")
        conn.close()
        return

    # Suppression
    conn.execute("""
        DELETE FROM activite_attendu
        WHERE attendu_id IN (
            SELECT id FROM attendu_scolaire WHERE type = 'disciplinaire'
        )
    """)

    # Nettoyage des cycles devenus orphelins (cycles uniquement dus aux attendus disciplinaires)
    # On garde les cycles encore justifies par au moins un attendu EDD
    conn.execute("""
        DELETE FROM activite_cycle
        WHERE (activite_id, cycle_id) NOT IN (
            SELECT DISTINCT aa.activite_id, a.cycle_id
            FROM activite_attendu aa
            JOIN attendu_scolaire a ON a.id = aa.attendu_id
        )
    """)

    conn.commit()

    print(f"  OK : {n_liens} association(s) disciplinaire(s) supprimee(s).")
    print("  Les associations EDD et les autres donnees sont intactes.")
    print()
    print("Vous pouvez relancer analyser_attendus_disciplinaires.py")

    conn.close()


if __name__ == "__main__":
    main()
