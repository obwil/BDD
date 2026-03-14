# =============================================================================
# migrate_excel.py
# =============================================================================
# Migre les données factuelles de l'Excel vers la base SQLite.
# Ne migre PAS : thématique, description, objectif, cycles
# (ces champs seront remplis par l'API Claude).
#
# Données migrées :
#   - Nom de l'activité
#   - Chemin du dossier (colonne B)
#   - Animée (colonne C)
#   - Météo (colonnes nuage/soleil/pluie/vent)
#   - Mois (colonnes J-F-M-A-M-J-J-A-S-O-N-D)
# =============================================================================

import sqlite3
import json
import openpyxl
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
CONFIG_PATH = SCRIPT_DIR / "config.json"
DB_PATH = SCRIPT_DIR / "activites.db"

MOIS_COLS = ["J", "F", "M", "A", "M.1", "J.1", "J.2", "A.1", "S", "O", "N", "D"]
MOIS_DB   = ["jan", "fev", "mar", "avr", "mai", "jun", "jul", "aou", "sep", "oct", "nov", "dec"]

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def col_val(row, idx):
    """Retourne la valeur d'une cellule ou chaîne vide."""
    v = row[idx].value
    return str(v).strip() if v else ""

def is_x(row, idx):
    """Retourne 1 si la cellule contient 'X' (insensible à la casse), sinon 0."""
    v = row[idx].value
    return 1 if v and str(v).strip().upper() == "X" else 0

def main():
    print("=" * 60)
    print("MIGRATION EXCEL -> SQLITE")
    print("=" * 60)

    config = load_config()
    excel_path = Path(config["excel_output"])

    if not excel_path.exists():
        print(f"ERREUR : Fichier Excel introuvable : {excel_path}")
        return

    if not DB_PATH.exists():
        print(f"ERREUR : Base SQLite introuvable : {DB_PATH}")
        print("   Lancez d'abord create_schema.py")
        return

    print(f"\nLecture de : {excel_path}")
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    inserted = 0
    skipped = 0
    errors = 0

    print("\nImport des activites...")
    for row in ws.iter_rows(min_row=2):
        nom = col_val(row, 0)
        if not nom:
            continue

        chemin    = col_val(row, 1)
        anime     = is_x(row, 2)
        # colonnes 3=thématique, 4=description, 5=objectif → ignorées
        lieu_raw  = col_val(row, 6)

        # Normaliser le lieu
        lieu = ""
        if lieu_raw:
            l = lieu_raw.lower()
            if "intérieur" in l and "extérieur" in l:
                lieu = "Intérieur/Extérieur"
            elif "extérieur" in l:
                lieu = "Extérieur"
            elif "intérieur" in l:
                lieu = "Intérieur"
            else:
                lieu = lieu_raw

        # Météo : non importée depuis Excel (sera déterminée par l'analyse Claude)
        nuage  = 0
        soleil = 0
        pluie  = 0
        vent   = 0

        # Mois (colonnes 15 à 26)
        mois = {}
        for i, m in enumerate(MOIS_DB):
            mois[m] = is_x(row, 15 + i)

        try:
            conn.execute("""
                INSERT OR IGNORE INTO activite (
                    nom, chemin_dossier, anime, lieu,
                    meteo_nuage, meteo_soleil, meteo_pluie, meteo_vent,
                    mois_jan, mois_fev, mois_mar, mois_avr,
                    mois_mai, mois_jun, mois_jul, mois_aou,
                    mois_sep, mois_oct, mois_nov, mois_dec
                ) VALUES (
                    :nom, :chemin, :anime, :lieu,
                    :nuage, :soleil, :pluie, :vent,
                    :jan, :fev, :mar, :avr,
                    :mai, :jun, :jul, :aou,
                    :sep, :oct, :nov, :dec
                )
            """, {
                "nom": nom, "chemin": chemin, "anime": anime, "lieu": lieu,
                "nuage": nuage, "soleil": soleil, "pluie": pluie, "vent": vent,
                **{m: mois[m] for m in MOIS_DB}
            })

            if conn.execute("SELECT changes()").fetchone()[0] > 0:
                inserted += 1
            else:
                skipped += 1
                print(f"  Ignore (deja presente) : {nom}")

        except Exception as e:
            errors += 1
            print(f"  ERREUR pour '{nom}' : {e}")

    conn.commit()
    conn.close()

    print(f"\n{'=' * 60}")
    print(f"OK {inserted} activité(s) importée(s)")
    if skipped:
        print(f"ATTENTION :  {skipped} activité(s) ignorée(s) (déjà présentes)")
    if errors:
        print(f"ERREUR : {errors} erreur(s)")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
