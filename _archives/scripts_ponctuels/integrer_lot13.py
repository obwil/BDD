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

# 1202 - Faire dancer des rameaux de pin
add(1202, "Int" + chr(233) + "rieur",
    "Les participants r" + chr(233) + "coltent de petits bouquets d\u2019aiguilles de pin et les posent " + chr(224) + " la verticale sur une table lisse. En tapotant la surface autour d\u2019eux sans les toucher, les aiguilles se mettent " + chr(224) + " vibrer et " + chr(224) + " \u00ab\u00a0danser\u00a0\u00bb sous l\u2019effet des vibrations et de l\u2019" + chr(233) + "lectricit" + chr(233) + " statique.",
    "D" + chr(233) + "couvrir les ph" + chr(233) + "nom" + chr(232) + "nes de vibration et d\u2019" + chr(233) + "lectricit" + chr(233) + " statique " + chr(224) + " travers une exp" + chr(233) + "rience surprenante avec des mat" + chr(233) + "riaux naturels.",
    "petit groupe", 20, tous,
    [103, 42], [3, 6],
    {"Cycle 1": [568], "Cycle 2": [646, 648], "Cycle 3": [774, 775]})

# 1203 - Faire de l art de peinture (raclette)
add(1203, "Int" + chr(233) + "rieur",
    "Les participants d" + chr(233) + "posent des gouttes de peinture sur un grand support et les " + chr(233) + "talent " + chr(224) + " la raclette en explorant diff" + chr(233) + "rents mouvements (droits, courbes, circulaires) et pressions. L\u2019activit" + chr(233) + " produit des \u0153uvres abstraites dynamiques avec des effets de m" + chr(233) + "langes imprévisibles.",
    "Explorer la physique des fluides et l\u2019expression artistique abstraite par la manipulation de la peinture " + chr(224) + " la raclette.",
    "individuel", 30, tous,
    [122], [15, 17],
    {"Cycle 1": [525, 526], "Cycle 2": [617, 618], "Cycle 3": [758, 762]})

# 1204 - Peinture avec du savon (art des bulles)
add(1204, "Int" + chr(233) + "rieur",
    "Les participants pr" + chr(233) + "parent un m" + chr(233) + "lange de peinture, savon et eau, soufflent dans le m" + chr(233) + "lange avec une paille pour cr" + chr(233) + "er une mousse color" + chr(233) + "e, puis pressent une feuille sur la mousse pour y transf" + chr(233) + "rer l\u2019empreinte unique des bulles.",
    "Explorer les propri" + chr(233) + "t" + chr(233) + "s des bulles et des m" + chr(233) + "langes, et cr" + chr(233) + "er des compositions abstraites " + chr(224) + " partir d\u2019empreintes de bulles color" + chr(233) + "es.",
    "individuel", 30, tous,
    [122, 235], [15, 17],
    {"Cycle 1": [525, 526], "Cycle 2": [617, 646], "Cycle 3": [758, 774]})

# 1205 - Peinture eau - encre de chine
add(1205, "Int" + chr(233) + "rieur",
    "Les participants versent de l\u2019encre de chine dans l\u2019eau ou sur un support humide pour cr" + chr(233) + "er des paysages abstraits que la diffusion guide naturellement. Des variantes incluent souffler l\u2019encre avec une paille, ajouter du sel pour des textures ou incliner le support.",
    "Explorer les propri" + chr(233) + "t" + chr(233) + "s de diffusion de l\u2019encre dans l\u2019eau et d" + chr(233) + "velopper l\u2019expression artistique en acceptant l\u2019imprévu.",
    "individuel", 30, tous,
    [122, 221], [15, 17],
    {"Cycle 1": [525], "Cycle 2": [617, 646], "Cycle 3": [758, 774]})

# 1206 - Percussions avec des coquilles de noix
add(1206, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants utilisent deux demi-coquilles de noix comme instruments de percussion naturels : ils les entrechoquent, les placent contre la bouche comme caisse de r" + chr(233) + "sonance et moduler la forme de la bouche pour varier les sons. Ils cr" + chr(233) + "ent ensuite des rythmes simples seuls ou en groupe.",
    "Exp" + chr(233) + "rimenter la percussion avec des mat" + chr(233) + "riaux naturels et d" + chr(233) + "couvrir le principe de caisse de r" + chr(233) + "sonance en explorant les variations sonores.",
    "individuel", 30, [10,11,12,1],
    [120, 134], [15, 2],
    {"Cycle 1": [529], "Cycle 2": [622, 624], "Cycle 3": [727]})

db.commit()
db.close()
print("Lot 13 termine.")
