import sqlite3

db_path = u'C:\\Users\\moina\\Dropbox\\Outils\\BDD activit\u00e9s\\_OUTIL\\activites.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Thématiques niveau 3 sous Biosphère, Cohésion sociale, Bien-être
print("=== THEMATIQUES niveau 3 ===")
cur.execute("""
    SELECT t1.nom as niv1, t2.nom as niv2, t3.id, t3.nom as niv3
    FROM thematique t3
    JOIN thematique t2 ON t3.parent_id = t2.id
    JOIN thematique t1 ON t2.parent_id = t1.id
    ORDER BY t1.nom, t2.nom, t3.nom
""")
for r in cur.fetchall():
    print(f"  {r[0]} > {r[1]} > [{r[2]}] {r[3]}")

conn.close()
