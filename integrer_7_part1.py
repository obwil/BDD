# -*- coding: utf-8 -*-
import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = u'C:\\Users\\moina\\Dropbox\\Outils\\BDD activit\u00e9s\\_OUTIL\\activites.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

mois_cols = ['mois_jan','mois_fev','mois_mar','mois_avr','mois_mai','mois_jun',
             'mois_jul','mois_aou','mois_sep','mois_oct','mois_nov','mois_dec']

def update_activite(aid, desc, obj, fmt, duree, mois, thematiques, objectifs):
    mois_vals = [1 if (i+1) in mois else 0 for i in range(12)]
    cur.execute("""UPDATE activite SET description=?,objectif_texte=?,format_groupe=?,duree_min=?,
        mois_jan=?,mois_fev=?,mois_mar=?,mois_avr=?,mois_mai=?,mois_jun=?,
        mois_jul=?,mois_aou=?,mois_sep=?,mois_oct=?,mois_nov=?,mois_dec=?
        WHERE id=?""",
        (desc, obj, fmt, duree, *mois_vals, aid))
    print(f"ID {aid}: champs de base OK")
    for tid in thematiques:
        cur.execute("SELECT 1 FROM activite_thematique WHERE activite_id=? AND thematique_id=?", (aid, tid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_thematique(activite_id,thematique_id) VALUES(?,?)", (aid, tid))
            print(f"  thematique {tid} ajoutee")
    for oid in objectifs:
        cur.execute("SELECT 1 FROM activite_objectif WHERE activite_id=? AND objectif_id=?", (aid, oid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_objectif(activite_id,objectif_id) VALUES(?,?)", (aid, oid))
            print(f"  objectif {oid} ajoute")
