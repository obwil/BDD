# =============================================================================
# deplacer_thematique.py
# =============================================================================
# Déplace une thématique dans l'arborescence en changeant son parent_id.
#
# Usage :
#   1. Modifier NOM_THEMATIQUE et NOM_NOUVEAU_PARENT ci-dessous
#   2. Lancer le script — en mode SIMULATION par défaut
#   3. Vérifier l'affichage, puis passer SIMULATION = False pour appliquer
#
# Mettre NOM_NOUVEAU_PARENT = None pour déplacer la thématique à la racine.
# =============================================================================

import sqlite3
from pathlib import Path

# ----------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------
SIMULATION = True  # False pour appliquer réellement

NOM_THEMATIQUE    = "Anatomie animale"       # Thématique à déplacer (nom exact)
NOM_NOUVEAU_PARENT = "Règne animal"  # Nouveau parent (nom exact), ou None pour racine

DB_PATH = Path(__file__).parent.parent / "activites.db"

# ----------------------------------------------------------------------------
# UTILITAIRES
# ----------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def trouver_thematique(conn, nom):
    rows = conn.execute(
        "SELECT id, nom, parent_id, niveau FROM thematique WHERE nom = ?", (nom,)
    ).fetchall()
    if not rows:
        return None
    if len(rows) > 1:
        print(f"  ATTENTION : plusieurs thématiques trouvées pour '{nom}' :")
        for r in rows:
            print(f"    id={r['id']}  parent_id={r['parent_id']}  niveau={r['niveau']}")
        print("  Précise le nom exact ou modifie le script pour cibler un id.")
        return None
    return rows[0]


def nom_parent(conn, parent_id):
    if parent_id is None:
        return "(racine)"
    row = conn.execute("SELECT nom FROM thematique WHERE id = ?", (parent_id,)).fetchone()
    return row["nom"] if row else f"(id={parent_id})"


def ancetres(conn, thematique_id):
    """Retourne la liste des ids ancêtres (pour détecter les cycles)."""
    ids = set()
    current = thematique_id
    while current is not None:
        row = conn.execute("SELECT parent_id FROM thematique WHERE id = ?", (current,)).fetchone()
        if not row:
            break
        current = row["parent_id"]
        if current is not None:
            ids.add(current)
    return ids


def calculer_niveau(conn, parent_id):
    if parent_id is None:
        return 0
    row = conn.execute("SELECT niveau FROM thematique WHERE id = ?", (parent_id,)).fetchone()
    return (row["niveau"] + 1) if row else 0


def mettre_a_jour_niveaux(conn, thematique_id, nouveau_niveau):
    """Met à jour récursivement les niveaux de la thématique et de ses descendants."""
    conn.execute(
        "UPDATE thematique SET niveau = ? WHERE id = ?", (nouveau_niveau, thematique_id)
    )
    enfants = conn.execute(
        "SELECT id FROM thematique WHERE parent_id = ?", (thematique_id,)
    ).fetchall()
    for enfant in enfants:
        mettre_a_jour_niveaux(conn, enfant["id"], nouveau_niveau + 1)


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------

def main():
    if not DB_PATH.exists():
        print(f"ERREUR : base de données introuvable : {DB_PATH}")
        return

    conn = get_db()

    # Trouver la thématique à déplacer
    cible = trouver_thematique(conn, NOM_THEMATIQUE)
    if not cible:
        print(f"ERREUR : thématique '{NOM_THEMATIQUE}' introuvable.")
        conn.close()
        return

    # Trouver le nouveau parent (ou None)
    nouveau_parent_id = None
    if NOM_NOUVEAU_PARENT is not None:
        np = trouver_thematique(conn, NOM_NOUVEAU_PARENT)
        if not np:
            print(f"ERREUR : thématique parent '{NOM_NOUVEAU_PARENT}' introuvable.")
            conn.close()
            return
        nouveau_parent_id = np["id"]

    # Vérifications
    if cible["parent_id"] == nouveau_parent_id:
        print(f"INFO : '{NOM_THEMATIQUE}' est déjà sous '{NOM_NOUVEAU_PARENT or 'racine'}'. Rien à faire.")
        conn.close()
        return

    if nouveau_parent_id == cible["id"]:
        print("ERREUR : impossible de définir une thématique comme son propre parent.")
        conn.close()
        return

    # Vérifier qu'on ne crée pas un cycle (le nouveau parent ne doit pas être
    # un descendant de la cible)
    descendants = set()
    def collecter_descendants(tid):
        enfants = conn.execute("SELECT id FROM thematique WHERE parent_id = ?", (tid,)).fetchall()
        for e in enfants:
            descendants.add(e["id"])
            collecter_descendants(e["id"])
    collecter_descendants(cible["id"])

    if nouveau_parent_id in descendants:
        print(f"ERREUR : '{NOM_NOUVEAU_PARENT}' est un descendant de '{NOM_THEMATIQUE}'.")
        print("  Ce déplacement créerait un cycle dans l'arbre — opération annulée.")
        conn.close()
        return

    # Calculer le nouveau niveau
    nouveau_niveau = calculer_niveau(conn, nouveau_parent_id)
    delta_niveau = nouveau_niveau - cible["niveau"]
    nb_descendants = len(descendants)

    # Afficher le résumé
    ancien_parent_nom = nom_parent(conn, cible["parent_id"])
    nouveau_parent_nom = NOM_NOUVEAU_PARENT or "(racine)"
    print()
    print("=" * 60)
    print("  DÉPLACEMENT DE THÉMATIQUE")
    print("=" * 60)
    print(f"  Thématique    : {cible['nom']}  (id={cible['id']})")
    print(f"  Ancien parent : {ancien_parent_nom}")
    print(f"  Nouveau parent: {nouveau_parent_nom}")
    print(f"  Niveau actuel : {cible['niveau']}  →  nouveau niveau : {nouveau_niveau}")
    if nb_descendants:
        print(f"  Descendants concernés : {nb_descendants} thématique(s) (niveaux mis à jour)")
    print()
    if SIMULATION:
        print("  MODE SIMULATION — aucune modification appliquée.")
        print("  Passer SIMULATION = False pour exécuter.")
    else:
        print("  MODE ÉCRITURE — les modifications vont être appliquées.")
    print("=" * 60)
    print()

    if SIMULATION:
        conn.close()
        return

    # Appliquer
    try:
        conn.execute(
            "UPDATE thematique SET parent_id = ?, niveau = ? WHERE id = ?",
            (nouveau_parent_id, nouveau_niveau, cible["id"])
        )
        # Mettre à jour les niveaux des descendants
        for desc_id in descendants:
            row = conn.execute(
                "SELECT niveau FROM thematique WHERE id = ?", (desc_id,)
            ).fetchone()
            if row:
                conn.execute(
                    "UPDATE thematique SET niveau = ? WHERE id = ?",
                    (row["niveau"] + delta_niveau, desc_id)
                )
        conn.commit()
        print(f"OK : '{NOM_THEMATIQUE}' déplacée sous '{nouveau_parent_nom}'.")
        if nb_descendants:
            print(f"     {nb_descendants} descendant(s) mis à jour.")
    except Exception as e:
        conn.rollback()
        print(f"ERREUR lors de la mise à jour : {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
