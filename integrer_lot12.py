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

# 1196 - Fleche polynesienne
add(1196, "Ext" + chr(233) + "rieur",
    "Les participants fabriquent une fl" + chr(232) + "che en bambou ou noisetier : ils taillent une pointe, r" + chr(233) + "alisent des ailettes en fente et une encoche pour la ficelle du propulseur. La fl" + chr(232) + "che est ensuite lanc" + chr(233) + "e " + chr(224) + " l\u2019aide d\u2019un propulseur " + chr(224) + " ficelle, technique polyn" + chr(233) + "sienne ancestrale.",
    "Fabriquer une fl" + chr(232) + "che traditionnelle et exp" + chr(233) + "rimenter le principe du propulseur " + chr(224) + " ficelle pour comprendre l\u2019influence de la technique sur la port" + chr(233) + "e.",
    "individuel", 60, tous,
    [128, 297], [15, 18],
    {"Cycle 2": [650, 617], "Cycle 3": [791, 797]})

# 1412 - Flute harmonique
add(1412, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants fabriquent une fl" + chr(251) + "te harmonique en PVC : ils d" + chr(233) + "coupent et assemblent un tube avec bouchon et biseau. En soufflant plus ou moins fort, ils produisent diff" + chr(233) + "rents harmoniques sans trous de jeu, explorant la s" + chr(233) + "rie harmonique naturelle.",
    "Comprendre la r" + chr(233) + "sonance des colonnes d\u2019air et la production des harmoniques en construisant une fl" + chr(251) + "te simple.",
    "individuel", 60, tous,
    [120], [15, 6],
    {"Cycle 2": [622, 624, 650], "Cycle 3": [727, 779]})

# 1198 - Flute a eau
add(1198, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants fabriquent une fl" + chr(251) + "te " + chr(224) + " eau en fixant un sifflet sur un b" + chr(226) + "ton puis en glissant une bouteille coupee autour. En plongeant et remontant la bouteille dans l\u2019eau tout en soufflant, la hauteur du son varie en temps r" + chr(233) + "el.",
    "Explorer le lien entre volume d\u2019air emprisonn" + chr(233) + " et hauteur du son en fabriquant un instrument " + chr(224) + " modulation continue.",
    "individuel", 45, tous,
    [120, 221], [15, 6],
    {"Cycle 2": [622, 624, 646], "Cycle 3": [727, 779]})

# 1199 - Harpe eolienne
add(1199, "Ext" + chr(233) + "rieur",
    "Les participants assemblent une harpe " + chr(233) + "olienne en tendant une ou plusieurs cordes sur un cadre en baguette de bois, maintenues par des ponts en caoutchouc. Pos" + chr(233) + "e en plein vent, la friction de l\u2019air sur les cordes provoque leur vibration et produit des sons m" + chr(233) + "lodieux.",
    "Comprendre le ph" + chr(233) + "nom" + chr(232) + "ne de vibration par friction du vent et fabriquer un instrument acoustique jou" + chr(233) + " par la nature.",
    "individuel", 45, tous,
    [120, 99], [15, 2],
    {"Cycle 2": [622, 624, 650], "Cycle 3": [727, 779]})

# 1200 - Toupie buissonniere
add(1200, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants percent une noix de part en part, la vident, et y ins" + chr(232) + "rent un b" + chr(226) + "tonnet " + chr(233) + "corc" + chr(233) + " et liss" + chr(233) + ". Une ficelle enroul" + chr(233) + "e autour du b" + chr(226) + "ton et tir" + chr(233) + "e brusquement lance la toupie en rotation.",
    "Fabriquer une toupie traditionnelle en mat" + chr(233) + "riaux naturels et exp" + chr(233) + "rimenter les principes du mouvement rotatif.",
    "individuel", 45, tous,
    [128], [15, 18],
    {"Cycle 1": [568, 569], "Cycle 2": [650, 617], "Cycle 3": [791, 797]})

db.commit()
db.close()
print("Lot 12 termine.")
