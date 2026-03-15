# =============================================================================
# importer_anime.py
# =============================================================================
# Lit le fichier Excel Activités_v2.xlsm et met à jour le champ anime=1
# dans la base SQLite pour toutes les activités marquées "Oui".
#
# Pour les activités non trouvées par correspondance exacte, propose
# automatiquement le nom le plus proche en base (similarité > SEUIL_SIMILARITE).
# =============================================================================

import sqlite3
import openpyxl
from pathlib import Path
from difflib import SequenceMatcher, get_close_matches

DB_PATH    = Path(__file__).parent.parent / "activites.db"
EXCEL_PATH = Path(r"C:\Users\moina\Dropbox\Animation\Activités v2\Activités v2.xlsm")

# Mettre False pour écrire réellement en base
SIMULATION = True

# Seuil de similarité pour les suggestions (0.0 à 1.0)
# 0.6 = assez permissif, 0.8 = strict
SEUIL_SIMILARITE = 0.9

# =============================================================================

def similarite(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def main():
    if not DB_PATH.exists():
        print(f"ERREUR : Base introuvable : {DB_PATH}")
        return
    if not EXCEL_PATH.exists():
        print(f"ERREUR : Fichier Excel introuvable : {EXCEL_PATH}")
        return

    print("Lecture du fichier Excel...")
    wb = openpyxl.load_workbook(str(EXCEL_PATH), read_only=True, keep_vba=True)
    ws = wb["Activités"]

    noms_anime = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        nom = row[0]
        anime = row[2]
        if nom and anime and str(anime).strip().lower() == "oui":
            noms_anime.add(str(nom).strip())

    print(f"{len(noms_anime)} activités marquées 'Oui' dans l'Excel\n")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    toutes = conn.execute("SELECT id, nom FROM activite ORDER BY nom").fetchall()
    noms_base = [a["nom"] for a in toutes]
    noms_base_lower = {a["nom"].lower(): a for a in toutes}

    # Correspondances exactes
    trouves_exact = []
    non_trouves = []
    for nom in sorted(noms_anime):
        match = noms_base_lower.get(nom.lower())
        if match:
            trouves_exact.append(match)
        else:
            non_trouves.append(nom)

    print(f"Correspondances exactes : {len(trouves_exact)}")
    for a in trouves_exact:
        print(f"  [OK] {a['nom']}")

    # Correspondances approchées pour les non trouvés
    trouves_approx = []  # liste de (nom_excel, activite_en_base)
    sans_suggestion = []

    if non_trouves:
        print(f"\nCorrespondances approchées ({len(non_trouves)} non trouvés) :")
        for nom in non_trouves:
            suggestions = get_close_matches(nom, noms_base, n=1, cutoff=SEUIL_SIMILARITE)
            if suggestions:
                meilleur = suggestions[0]
                score = similarite(nom, meilleur)
                match = noms_base_lower[meilleur.lower()]
                trouves_approx.append((nom, match))
                print(f"  [~] '{nom}'")
                print(f"       → '{meilleur}' (similarité: {score:.0%})")
            else:
                sans_suggestion.append(nom)
                print(f"  [??] '{nom}' — aucune suggestion trouvée")

    if sans_suggestion:
        print(f"\nActivités sans suggestion ({len(sans_suggestion)}) :")
        for nom in sans_suggestion:
            print(f"  [X] {nom}")

    total = len(trouves_exact) + len(trouves_approx)
    print(f"\nTotal à mettre à jour : {total} activités")
    print(f"  - {len(trouves_exact)} correspondances exactes")
    print(f"  - {len(trouves_approx)} correspondances approchées")
    if sans_suggestion:
        print(f"  - {len(sans_suggestion)} sans correspondance (ignorées)")

    if SIMULATION:
        print(f"\n>>> Simulation : {total} activité(s) seraient mises à anime=1.")
        print("    Vérifiez les correspondances approchées ci-dessus.")
        print("    Mettre SIMULATION = False pour appliquer.")
        conn.close()
        return

    # Mise à jour
    ok = 0
    for a in trouves_exact:
        conn.execute("UPDATE activite SET anime = 1 WHERE id = ?", (a["id"],))
        ok += 1
    for _, a in trouves_approx:
        conn.execute("UPDATE activite SET anime = 1 WHERE id = ?", (a["id"],))
        ok += 1

    conn.commit()
    conn.close()
    print(f"\n{ok} activité(s) mises à jour (anime=1).")
    print("Terminé.")


if __name__ == "__main__":
    main()
