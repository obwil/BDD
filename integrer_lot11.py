import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
db = sqlite3.connect(r"C:\Users\moina\Dropbox\Outils\BDD activit" + chr(233) + r"s\_OUTIL\activites.db")
cur = db.cursor()
cur.execute("SELECT id, nom FROM cycle")
cycles = {r[1]: r[0] for r in cur.fetchall()}

def add(aid, lieu, desc, obj_txt, fmt, duree, mois, themes, objectifs, cycles_attendus):
    mois_vals = [1 if (i+1) in mois else 0 for i in range(12)]
    cur.execute("""UPDATE activite SET lieu=?,description=?,objectif_texte=?,format_groupe=?,duree_min=?,
        mois_jan=?,mois_fev=?,mois_mar=?,mois_avr=?,mois_mai=?,mois_jun=?,
        mois_jul=?,mois_aou=?,mois_sep=?,mois_oct=?,mois_nov=?,mois_dec=? WHERE id=?""",
        (lieu, desc, obj_txt, fmt, duree, *mois_vals, aid))
    for tid in themes:
        cur.execute("SELECT 1 FROM activite_thematique WHERE activite_id=? AND thematique_id=?", (aid,tid))
        if not cur.fetchone(): cur.execute("INSERT INTO activite_thematique VALUES(?,?)", (aid,tid))
    for oid in objectifs:
        cur.execute("SELECT 1 FROM activite_objectif WHERE activite_id=? AND objectif_id=?", (aid,oid))
        if not cur.fetchone(): cur.execute("INSERT INTO activite_objectif VALUES(?,?)", (aid,oid))
    for cnom, atts in cycles_attendus.items():
        cid = cycles[cnom]
        cur.execute("SELECT 1 FROM activite_cycle WHERE activite_id=? AND cycle_id=?", (aid,cid))
        if not cur.fetchone(): cur.execute("INSERT INTO activite_cycle VALUES(?,?)", (aid,cid))
        cur.execute("SELECT 1 FROM activite_cycle_analysee WHERE activite_id=? AND cycle_id=?", (aid,cid))
        if not cur.fetchone(): cur.execute("INSERT INTO activite_cycle_analysee VALUES(?,?,'ok')", (aid,cid))
        else: cur.execute("UPDATE activite_cycle_analysee SET statut='ok' WHERE activite_id=? AND cycle_id=?", (aid,cid))
        for att in atts:
            cur.execute("SELECT 1 FROM activite_attendu WHERE activite_id=? AND attendu_id=?", (aid,att))
            if not cur.fetchone(): cur.execute("INSERT INTO activite_attendu VALUES(?,?)", (aid,att))
    print(f"ID {aid} OK")

tous = list(range(1,13))

# 1190 - Canera (rasca-tripas)
add(1190, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants d" + chr(233) + "coupent 7 morceaux de bambou perc" + chr(233) + "s et les enfilent sur une corde pour cr" + chr(233) + "er une can" + chr(233) + "ra. Un racleur en bambou fendu fend" + chr(233) + " en lamelles est frott" + chr(233) + " contre les pi" + chr(232) + "ces assemble pour produire un son rythmique vibrant.",
    "Fabriquer un instrument " + chr(224) + " friction traditionnel en bambou et explorer la sonor" + chr(233) + "it" + chr(233) + " des mat" + chr(233) + "riaux naturels assembl" + chr(233) + "s.",
    "individuel", 60, tous,
    [120, 128], [15, 18],
    {"Cycle 2": [622, 624], "Cycle 3": [727, 725]})

# 1192 - Castanola de cana (canyoto)
add(1192, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants s" + chr(233) + "lectionnent une tige de bambou sec, la d" + chr(233) + "coupent et la fendent pour fabriquer un canyoto (castagnette traditionnelle espagnole). L\u2019instrument se tient en main et produit un claquement rythmique caract" + chr(233) + "ristique.",
    "Fabriquer un instrument de percussion traditionnel espagnol en bambou et d" + chr(233) + "couvrir ses propri" + chr(233) + "t" + chr(233) + "s acoustiques.",
    "individuel", 60, tous,
    [120, 128], [15, 18],
    {"Cycle 2": [622, 624], "Cycle 3": [727, 725]})

# 1193 - Chenille qui bouge sur une feuille
add(1193, "Int" + chr(233) + "rieur",
    "Les participants fabriquent une feuille en papier pli" + chr(233) + " en accord" + chr(233) + "on et une chenille articul" + chr(233) + "e en tube de papier frois" + chr(233) + ". La chenille est fix" + chr(233) + "e sur une tige au dos de la feuille, lui permettant de glisser et de simuler son mouvement.",
    "Explorer l\u2019anatomie des chenilles et la structure des feuilles " + chr(224) + " travers une activit" + chr(233) + " de cr" + chr(233) + "ation manuelle avec m" + chr(233) + "canisme.",
    "individuel", 30, tous,
    [22, 63], [15, 5],
    {"Cycle 1": [523, 564], "Cycle 2": [617, 648], "Cycle 3": [784, 788]})

# 1194 - Citare a tube en bambou
add(1194, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants taillent des lamelles longitudinales dans la paroi d\u2019un tube de bambou sans les d" + chr(233) + "tacher, puis ins" + chr(232) + "rent de petits ponts dessous pour les sur" + chr(233) + "lever et cr" + chr(233) + "er une tension. Frapp" + chr(233) + "es avec des baguettes, ces \u00ab\u00a0cordes\u00a0\u00bb produisent des notes distinctes.",
    "Fabriquer une cithare " + chr(224) + " tube en bambou et comprendre le lien entre tension d\u2019une lamelle et hauteur du son.",
    "individuel", 75, tous,
    [120, 128], [15, 18],
    {"Cycle 2": [622, 624, 650], "Cycle 3": [727, 779]})

# 1195 - Double anche
add(1195, "Int" + chr(233) + "rieur",
    "Les participants fabriquent une anche double en taillant deux lamelles de roseau (Arundo donax) et en les liant " + chr(224) + " leur base sur un tube. En soufflant entre les deux lamelles, elles vibrent l\u2019une contre l\u2019autre et produisent le son caract" + chr(233) + "ristique des hautbois traditionnels.",
    "Comprendre le principe acoustique des instruments " + chr(224) + " anche double et s\u2019initier " + chr(224) + " la lutherie des instruments " + chr(224) + " vent traditionnels.",
    "individuel", 60, tous,
    [120, 128], [15, 2],
    {"Cycle 3": [727, 725, 779]})

db.commit()
db.close()
print("Lot 11 termine.")
