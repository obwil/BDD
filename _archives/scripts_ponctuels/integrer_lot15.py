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

# 1215 - Fusee avec un brin d herbe
add(1215, "Ext" + chr(233) + "rieur",
    "Les participants s" + chr(233) + "lectionnent deux brins de jonc : le plus long est fendu au centre (lanceur) et l\u2019extr" + chr(233) + "mit" + chr(233) + " effile du plus court y est ins" + chr(233) + "r" + chr(233) + " (projectile). En pliant le lanceur et en l" + chr(226) + "chant brusquement, la tension propulse le brin dans les airs.",
    "Exp" + chr(233) + "rimenter un m" + chr(233) + "canisme de propulsion naturel avec des tiges v" + chr(233) + "g" + chr(233) + "tales et comprendre les principes de tension et de lib" + chr(233) + "ration d\u2019" + chr(233) + "nergie.",
    "individuel", 20, tous,
    [63, 297], [16, 6],
    {"Cycle 2": [646, 650], "Cycle 3": [777, 778, 779]})

# 1217 - Feu d artifice zeste d orange
add(1217, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "En pressant un zeste d\u2019orange fra" + chr(238) + "s au-dessus d\u2019une bougie, les huiles essentielles s\u2019enflamment en produisant un jet d\u2019" + chr(233) + "tincelles spectaculaire. Les participants d" + chr(233) + "couvrent le limon" + chr(232) + "ne et les propri" + chr(233) + "t" + chr(233) + "s inflammables des huiles essentielles d\u2019agrumes.",
    "D" + chr(233) + "couvrir les propri" + chr(233) + "t" + chr(233) + "s chimiques des huiles essentielles des agrumes " + chr(224) + " travers une d" + chr(233) + "monstration spectaculaire.",
    "petit groupe", 15, tous,
    [135, 234], [6, 3],
    {"Cycle 2": [646, 648], "Cycle 3": [774, 775]})

# 764 - Concept kids animaux
add(764, "Int" + chr(233) + "rieur",
    "Jeu coop" + chr(233) + "ratif o" + chr(249) + " un joueur fait deviner un animal en pla" + chr(231) + "ant des pions sur des pictogrammes (habitat, alimentation, taille, mode de d" + chr(233) + "placement) sans parler. Les autres observent les indices et proposent des animaux.",
    "D" + chr(233) + "velopper la connaissance des animaux et de leurs caract" + chr(233) + "ristiques, et travailler la communication non verbale et la coop" + chr(233) + "ration.",
    "petit groupe", 30, tous,
    [20, 37], [4, 6],
    {"Cycle 1": [564, 565, 522], "Cycle 2": [648, 638], "Cycle 3": [784]})

# 699 - Jeu d orientation La grande aventure des plantes
add(699, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Jeu d\u2019orientation en 5 ateliers (jardinier, g" + chr(233) + "ographe, historien, explorateur, d" + chr(233) + "tective) autour de l\u2019origine des plantes alimentaires. Les " + chr(233) + "quipes associent des aliments " + chr(224) + " leurs plantes, retrouvent leurs origines g" + chr(233) + "ographiques et historiques, et d" + chr(233) + "couvrent les routes commerciales.",
    "D" + chr(233) + "couvrir l\u2019origine g" + chr(233) + "ographique et historique des plantes alimentaires en enquêtant par ateliers.",
    "petit groupe", 90, tous,
    [49, 119], [4, 12],
    {"Cycle 2": [648, 653, 657], "Cycle 3": [784, 764, 771]})

# 701 - Jeu d orientation sur les couleurs dans la nature
add(701, "Ext" + chr(233) + "rieur",
    "Circuit d\u2019orientation en 10 " + chr(233) + "tapes dans un espace naturel autour de la couleur dans la nature : camouflage, communication, photo" + chr(231) + "ynthèse, fleurs, plantes tinctoriales. Les " + chr(233) + "quipes r" + chr(233) + "pondent " + chr(224) + " des questions " + chr(224) + " chaque balise.",
    "D" + chr(233) + "couvrir les fonctions " + chr(233) + "cologiques de la couleur chez les " + chr(234) + "tres vivants : camouflage, communication, pollinisation, plantes tinctoriales.",
    "petit groupe", 120, tous,
    [133, 37, 63], [4, 6],
    {"Cycle 2": [648, 574], "Cycle 3": [784, 806]})

db.commit()
db.close()
print("Lot 15 termine.")
