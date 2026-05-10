import sqlite3

db_path = u'C:\\Users\\moina\\Dropbox\\Outils\\BDD activit\u00e9s\\_OUTIL\\activites.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Objectifs
print("=== OBJECTIFS ===")
cur.execute("SELECT id, nom FROM objectif ORDER BY id")
for r in cur.fetchall():
    print(f"  {r[0]} | {r[1]}")

# Thématiques (premier niveau + niveau 2)
print("\n=== THEMATIQUES (niveaux 1 et 2) ===")
cur.execute("""
    SELECT t1.id, t1.nom, t2.id, t2.nom 
    FROM thematique t1
    LEFT JOIN thematique t2 ON t2.parent_id = t1.id
    WHERE t1.parent_id IS NULL
    ORDER BY t1.nom, t2.nom
""")
rows = cur.fetchall()
current_parent = None
for r in rows:
    if r[0] != current_parent:
        current_parent = r[0]
        print(f"\n  [{r[0]}] {r[1]}")
    if r[2]:
        print(f"    [{r[2]}] {r[3]}")

# Format groupe valeurs possibles
print("\n=== FORMAT GROUPE (valeurs existantes) ===")
cur.execute("SELECT DISTINCT format_groupe FROM activite WHERE format_groupe IS NOT NULL ORDER BY format_groupe")
for r in cur.fetchall():
    print(f"  {r[0]}")

conn.close()
