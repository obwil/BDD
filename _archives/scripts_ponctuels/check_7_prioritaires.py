import sqlite3

db_path = u'C:\\Users\\moina\\Dropbox\\Outils\\BDD activit\u00e9s\\_OUTIL\\activites.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Les 7 avec thematique/cycle - chemin dossier + thematiques + cycles
cur.execute("""
    SELECT DISTINCT a.id, a.nom, a.chemin_dossier, a.objectif_texte, a.format_groupe,
                    a.duree_min, a.meteo_soleil, a.meteo_nuage, a.meteo_pluie, a.meteo_vent, a.meteo_nuit
    FROM activite a
    WHERE (a.description IS NULL OR a.description = '')
    AND (
        EXISTS (SELECT 1 FROM activite_thematique at2 WHERE at2.activite_id = a.id)
        OR EXISTS (SELECT 1 FROM activite_cycle ac WHERE ac.activite_id = a.id)
    )
    ORDER BY a.nom
""")
rows = cur.fetchall()
cols = ['id','nom','chemin_dossier','objectif_texte','format_groupe','duree_min',
        'meteo_soleil','meteo_nuage','meteo_pluie','meteo_vent','meteo_nuit']

for r in rows:
    d = dict(zip(cols, r))
    print("---")
    for k,v in d.items():
        print(f"  {k}: {v}")
    
    # Thematiques
    cur.execute("""
        SELECT t.nom FROM thematique t
        JOIN activite_thematique at2 ON at2.thematique_id = t.id
        WHERE at2.activite_id = ?
    """, (d['id'],))
    themes = [x[0] for x in cur.fetchall()]
    print(f"  thematiques: {themes}")
    
    # Cycles
    cur.execute("""
        SELECT c.nom FROM cycle c
        JOIN activite_cycle ac ON ac.cycle_id = c.id
        WHERE ac.activite_id = ?
    """, (d['id'],))
    cycles = [x[0] for x in cur.fetchall()]
    print(f"  cycles: {cycles}")

conn.close()
