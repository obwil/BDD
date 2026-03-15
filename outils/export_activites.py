# export_activites.py
# Exporte nom, description et thematiques de chaque activite vers un fichier Excel.

import sqlite3
import pandas as pd
from pathlib import Path

# DB et export a la racine de _OUTIL, un niveau au-dessus de outil/
DB_PATH = Path(__file__).parent.parent / "activites.db"
OUTPUT_PATH = Path(__file__).parent.parent / "export_tags.xlsx"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    activites = conn.execute("""
        SELECT id, nom, description
        FROM activite
        ORDER BY nom COLLATE NOCASE
    """).fetchall()

    thematiques_map = {}
    rows = conn.execute("""
        SELECT at.activite_id, t.nom
        FROM activite_thematique at
        JOIN thematique t ON t.id = at.thematique_id
        ORDER BY at.activite_id, t.nom
    """).fetchall()
    for row in rows:
        thematiques_map.setdefault(row["activite_id"], []).append(row["nom"])

    conn.close()

    data = []
    for a in activites:
        thematiques = thematiques_map.get(a["id"], [])
        data.append({
            "ID": a["id"],
            "Nom": a["nom"],
            "Description": a["description"] or "",
            "Thematiques": " | ".join(thematiques),
            "Tags suggeres": ""
        })

    df = pd.DataFrame(data)

    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Activites")
        ws = writer.sheets["Activites"]

        ws.column_dimensions["A"].width = 6
        ws.column_dimensions["B"].width = 40
        ws.column_dimensions["C"].width = 80
        ws.column_dimensions["D"].width = 60
        ws.column_dimensions["E"].width = 30

        from openpyxl.styles import Alignment
        for cell in ws["C"][1:]:
            cell.alignment = Alignment(wrap_text=True)

    print(f"Export termine : {OUTPUT_PATH}")
    print(f"{len(data)} activites exportees.")

if __name__ == "__main__":
    main()
