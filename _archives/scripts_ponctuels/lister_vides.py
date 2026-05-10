# -*- coding: utf-8 -*-
import sqlite3, sys
sys.stdout.reconfigure(encoding="utf-8")

db_path = u"C:\\Users\\moina\\Dropbox\\Outils\\BDD activit\u00e9s\\_OUTIL\\activites.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
    SELECT a.id, a.nom, a.chemin_dossier
    FROM activite a
    WHERE (a.description IS NULL OR a.description = "")
    AND NOT EXISTS (SELECT 1 FROM activite_thematique at2 WHERE at2.activite_id = a.id)
    AND NOT EXISTS (SELECT 1 FROM activite_cycle ac WHERE ac.activite_id = a.id)
    ORDER BY a.nom
""")
rows = cur.fetchall()
print(f"Total: {len(rows)}")
for r in rows:
    chemin = r[2].replace("file:///", "").replace("/", "\\") if r[2] else ""
    print(f"{r[0]}|{r[1]}|{chemin}")

conn.close()
