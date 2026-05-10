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

# 1270 - Baseball buissonnier (pirulo)
add(1270, "Ext" + chr(233) + "rieur",
    "Les participants fabriquent un pirulo (petit b" + chr(226) + "ton effi" + chr(233) + " aux deux extr" + chr(233) + "mit" + chr(233) + "s) et une batte en bois taill" + chr(233) + "s sur place. Ils jouent ensuite : le pirulo est frapp" + chr(233) + " au sol pour le faire sauter, puis " + chr(224) + " nouveau en l\u2019air avec la batte.",
    "S\u2019initier " + chr(224) + " la sculpture sur bois et d" + chr(233) + "couvrir un jeu d\u2019adresse traditionnel pr" + chr(233) + "sent dans de nombreuses cultures.",
    "individuel", 75, tous,
    [128, 125], [15, 16],
    {"Cycle 2": [626, 628], "Cycle 3": [734, 735]})

# 1222 - Jeu de deplacement d animaux en papier
add(1222, "Int" + chr(233) + "rieur",
    "Les participants d" + chr(233) + "coupent et plient une bande de papier cartonn" + chr(233) + " pour cr" + chr(233) + "er un animal avec des pattes en accord" + chr(233) + "on (ressorts). Une pression sur l\u2019arri" + chr(232) + "re actionne les pattes et fait avancer l\u2019animal sur une surface lisse.",
    "Explorer un m" + chr(233) + "canisme de mouvement simple par pliage et comprendre le lien entre forme et d" + chr(233) + "placement.",
    "individuel", 25, tous,
    [37, 297], [15, 5],
    {"Cycle 1": [523, 568], "Cycle 2": [617, 650], "Cycle 3": [791, 796]})

# 1223 - Jeu de la guise (bâtons)
add(1223, "Ext" + chr(233) + "rieur",
    "La guise (Gilli-Danda, Dandi Biyo) est un jeu traditionnel d\u2019Asie du Sud : un grand b" + chr(226) + "ton (batte) frappe un petit b" + chr(226) + "ton taill" + chr(233) + " en pointe (gilli) pour le faire sauter, puis le propulse au loin. Les participants fabriquent les b" + chr(226) + "tons sur place et jouent.",
    "D" + chr(233) + "couvrir un jeu traditionnel international, d" + chr(233) + "velopper la coordination \u0153il-main et la motricit" + chr(233) + " globale.",
    "grand groupe", 60, tous,
    [128, 125], [16, 10],
    {"Cycle 2": [626, 628, 634], "Cycle 3": [734, 744]})

# 1224 - Jeu de plateau - Achi (Ghana)
add(1224, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Achi est un jeu de strat" + chr(233) + "gie traditionnel ghan" + chr(233) + "en pour 2 joueurs. Sur un plateau de 9 points, chaque joueur place alternativement ses 4 pions puis les d" + chr(233) + "place pour aligner 3 pions cons" + chr(233) + "cutifs, tout en bloquant l\u2019adversaire.",
    "D" + chr(233) + "velopper la r" + chr(233) + "flexion tactique et d" + chr(233) + "couvrir un jeu de strat" + chr(233) + "gie de la tradition orale africaine.",
    "binome", 20, tous,
    [128, 125], [16],
    {"Cycle 1": [522], "Cycle 2": [634, 644], "Cycle 3": [744, 756]})

# 1226 - Jeu de plateau - len choa (tigre et leopards)
add(1226, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Len Choa (\u00ab\u00a0Tigre et L" + chr(233) + "opards\u00a0\u00bb) est un jeu de plateau asiatique pour 2 joueurs. Sur un plateau triangulaire, le tigre tente d\u2019" + chr(233) + "liminer les 6 l" + chr(233) + "opards en sautant par-dessus, tandis que les l" + chr(233) + "opards cherchent " + chr(224) + " l\u2019encercler.",
    "D" + chr(233) + "velopper la strat" + chr(233) + "gie et la prise de d" + chr(233) + "cision " + chr(224) + " travers un jeu de plateau traditionnel d\u2019Asie du Sud.",
    "binome", 20, tous,
    [128, 125], [16],
    {"Cycle 2": [634, 644], "Cycle 3": [744, 756]})

db.commit()
db.close()
print("Lot 16 termine.")
