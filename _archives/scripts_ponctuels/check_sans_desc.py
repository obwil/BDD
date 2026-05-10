import sqlite3

db_path = u'C:\\Users\\moina\\Dropbox\\Outils\\BDD activit\u00e9s\\_OUTIL\\activites.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Total sans description
cur.execute("SELECT COUNT(*) FROM activite WHERE description IS NULL OR description = ''")
total = cur.fetchone()[0]
print(f"Total sans description: {total}")

# Sans desc ET avec thematique ou cycle
cur.execute("""
    SELECT DISTINCT a.id, a.nom
    FROM activite a
    WHERE (a.description IS NULL OR a.description = '')
    AND (
        EXISTS (SELECT 1 FROM activite_thematique at2 WHERE at2.activite_id = a.id)
        OR EXISTS (SELECT 1 FROM activite_cycle ac WHERE ac.activite_id = a.id)
    )
    ORDER BY a.nom
""")
avec = cur.fetchall()
print(f"\nSans desc MAIS avec thematique/cycle: {len(avec)}")
for r in avec:
    print(f"  {r[0]} | {r[1]}")

# Complètement vides (sans desc, sans thematique, sans cycle)
cur.execute("""
    SELECT a.id, a.nom, a.chemin_dossier
    FROM activite a
    WHERE (a.description IS NULL OR a.description = '')
    AND NOT EXISTS (SELECT 1 FROM activite_thematique at2 WHERE at2.activite_id = a.id)
    AND NOT EXISTS (SELECT 1 FROM activite_cycle ac WHERE ac.activite_id = a.id)
    ORDER BY a.nom
    LIMIT 10
""")
vides = cur.fetchall()
print(f"\nPremières activités complètement vides (échantillon 10):")
for r in vides:
    print(f"  {r[0]} | {r[1]}")

conn.close()
