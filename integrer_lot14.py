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

# 1207 - Light painting
add(1207, "Int" + chr(233) + "rieur",
    "En longue exposition photographique dans un espace sombre, les participants bougent des lampes torches ou LEDs pour cr" + chr(233) + "er des traces de lumi" + chr(232) + "re figer sur la photo. L\u2019activit" + chr(233) + " explore les liens entre mouvement, lumi" + chr(232) + "re et image photographique.",
    "Explorer les propri" + chr(233) + "t" + chr(233) + "s de la lumi" + chr(232) + "re et de la photographie en longue exposition, et d" + chr(233) + "velopper la cr" + chr(233) + "ativit" + chr(233) + " artistique.",
    "petit groupe", 45, tous,
    [229, 122], [15, 17],
    {"Cycle 2": [617, 618], "Cycle 3": [758, 781]})

# 1210 - Grenouille sauteuse
add(1210, "Int" + chr(233) + "rieur",
    "Les participants fabriquent une grenouille sauteuse " + chr(224) + " partir d\u2019un rouleau de papier toilette recycl" + chr(233) + " : ils d" + chr(233) + "coupent les pattes, fa" + chr(231) + "onnent la bouche, d" + chr(233) + "corent et plient les pattes en ressort. Une pression sur le dos provoque le saut.",
    "Fabriquer un objet m" + chr(233) + "canique simple inspir" + chr(233) + " d\u2019un animal et d" + chr(233) + "couvrir les amphibiens " + chr(224) + " travers la cr" + chr(233) + "ation.",
    "individuel", 25, tous,
    [20, 297], [15, 5],
    {"Cycle 1": [523, 569], "Cycle 2": [617, 648], "Cycle 3": [784, 791]})

# 1211 - Faire sortir les vers de terre
add(1211, "Ext" + chr(233) + "rieur",
    "Les participants utilisent des techniques pour faire remonter les vers de terre sans creuser : vibrations dans le sol (bâton frottë sur une fourche — \u00ab\u00a0worm grunting\u00a0\u00bb), humidification abondante. Les vers observ" + chr(233) + "s sont compt" + chr(233) + "s, " + chr(233) + "tudi" + chr(233) + "s (anatomie, locomotion, r" + chr(244) + "le dans le sol) puis relâch" + chr(233) + "s.",
    "D" + chr(233) + "couvrir les vers de terre et leur r" + chr(244) + "le dans la vie du sol, et exp" + chr(233) + "rimenter des techniques d\u2019observation faunistique non-invasives.",
    "petit groupe", 40, [3,4,5,9,10,11],
    [32, 162], [3, 4],
    {"Cycle 1": [564, 565], "Cycle 2": [648, 574], "Cycle 3": [806, 807]})

# 158 - Test de personnalite nature
add(158, "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants r" + chr(233) + "pondent " + chr(224) + " un questionnaire " + chr(224) + " choix multiples pour d" + chr(233) + "couvrir leur profil nature parmi six types : Aventurier de la For" + chr(234) + "t, Artiste de la Nature, Naturaliste, Protecteur des Animaux, Jardinier en Herbe, Cueilleur. Des cartes et illustrations imprimables compl" + chr(232) + "tent l\u2019activit" + chr(233) + ".",
    "D" + chr(233) + "couvrir son rapport personnel " + chr(224) + " la nature et identifier ses centres d\u2019int" + chr(233) + "r" + chr(234) + "t en lien avec le vivant.",
    "individuel", 25, tous,
    [1, 239], [1, 5],
    {"Cycle 1": [501], "Cycle 2": [604, 639], "Cycle 3": [714, 749]})

# 1213 - Arche de pierre
add(1213, "Ext" + chr(233) + "rieur",
    "Les participants construisent une arche de pierre en " + chr(233) + "quilibre sans liant : ils s" + chr(233) + "lectionnent des pierres trap" + chr(233) + "zo" + chr(239) + "dales, " + chr(233) + "rigent deux piliers puis courbent progressivement les rang" + chr(233) + "es vers le centre jusqu\u2019" + chr(224) + " la pose de la cl" + chr(233) + " de vo" + chr(251) + "te. L\u2019activit" + chr(233) + " d" + chr(233) + "veloppe la patience et la compr" + chr(233) + "hension de la statique.",
    "Explorer les principes de la statique et de la compression " + chr(224) + " travers la construction d\u2019une arche en pierre en " + chr(233) + "quilibre.",
    "individuel", 45, tous,
    [75, 76], [18, 6],
    {"Cycle 2": [650, 651], "Cycle 3": [774, 775, 797]})

db.commit()
db.close()
print("Lot 14 termine.")
