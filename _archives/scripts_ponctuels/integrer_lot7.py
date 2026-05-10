import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
db = sqlite3.connect(r"C:\Users\moina\Dropbox\Outils\BDD activit" + chr(233) + r"s\_OUTIL\activites.db")
cur = db.cursor()
cur.execute("SELECT id, nom FROM cycle")
cycles = {r[1]: r[0] for r in cur.fetchall()}

def add(aid, lieu, desc, obj_txt, fmt, duree, mois, themes, objectifs, ca, meteo=None):
    mois_vals = [1 if (i+1) in mois else 0 for i in range(12)]
    m = meteo or {}
    cur.execute("""UPDATE activite SET lieu=?,description=?,objectif_texte=?,format_groupe=?,duree_min=?,
        mois_jan=?,mois_fev=?,mois_mar=?,mois_avr=?,mois_mai=?,mois_jun=?,
        mois_jul=?,mois_aou=?,mois_sep=?,mois_oct=?,mois_nov=?,mois_dec=?,
        meteo_soleil=?,meteo_nuage=?,meteo_pluie=?,meteo_vent=?,meteo_nuit=?
        WHERE id=?""",
        (lieu,desc,obj_txt,fmt,duree,*mois_vals,
         m.get("soleil",0),m.get("nuage",0),m.get("pluie",0),m.get("vent",0),m.get("nuit",0),aid))
    for tid in themes:
        cur.execute("SELECT 1 FROM activite_thematique WHERE activite_id=? AND thematique_id=?",(aid,tid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_thematique(activite_id,thematique_id) VALUES(?,?)",(aid,tid))
    for oid in objectifs:
        cur.execute("SELECT 1 FROM activite_objectif WHERE activite_id=? AND objectif_id=?",(aid,oid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_objectif(activite_id,objectif_id) VALUES(?,?)",(aid,oid))
    for cn, atts in ca.items():
        cid = cycles[cn]
        cur.execute("SELECT 1 FROM activite_cycle WHERE activite_id=? AND cycle_id=?",(aid,cid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_cycle(activite_id,cycle_id) VALUES(?,?)",(aid,cid))
        cur.execute("SELECT 1 FROM activite_cycle_analysee WHERE activite_id=? AND cycle_id=?",(aid,cid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_cycle_analysee(activite_id,cycle_id,statut) VALUES(?,?,'ok')",(aid,cid))
        else:
            cur.execute("UPDATE activite_cycle_analysee SET statut='ok' WHERE activite_id=? AND cycle_id=?",(aid,cid))
        for att in atts:
            cur.execute("SELECT 1 FROM activite_attendu WHERE activite_id=? AND attendu_id=?",(aid,att))
            if not cur.fetchone():
                cur.execute("INSERT INTO activite_attendu(activite_id,attendu_id) VALUES(?,?)",(aid,att))
    print(f"ID {aid} OK")

tous = list(range(1,13))
IE = "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur"
I = "Int" + chr(233) + "rieur"
E = "Ext" + chr(233) + "rieur"

# 1237 - Kazoo en houx
add(1237, E,
    "Les participants s\u00e9lectionnent de jeunes feuilles de houx et pr\u00e9parent une membrane vibrante en d\u00e9chirant d\u00e9licatement le limbe de part et d\u2019autre de la nervure centrale. En soufflant ou en fredonnant dans la feuille pli\u00e9e, la membrane produit un son aigu caract\u00e9ristique.",
    "Fabriquer un instrument rudimentaire \u00e0 partir d\u2019une feuille de houx et explorer les propri\u00e9t\u00e9s sonores des v\u00e9g\u00e9taux.",
    "individuel", 30, [10,11,12,1,2,3],  # automne-hiver (houx)
    [120,49,134],  # Musique du monde, Groupes vegetaux, Audition
    [15,5],
    {"Cycle 1":[523,531,507,564,565],
     "Cycle 2":[622,623,624,648],
     "Cycle 3":[725,727,728,784]})

# 892 - Land art
add(892, E,
    "Les participants collectent des \u00e9l\u00e9ments naturels (pierres, feuilles, brindilles, fleurs, graines, mousse) et cr\u00e9ent des compositions artistiques \u00e9ph\u00e9m\u00e8res directement dans la nature, en solo ou en \u00e9quipe. Les \u0153uvres peuvent repr\u00e9senter des formes abstraites, des visages, des mandalas ou des sc\u00e8nes.",
    "D\u00e9velopper le regard artistique, la cr\u00e9ativit\u00e9 et le lien affectif avec la nature en cr\u00e9ant des \u0153uvres \u00e9ph\u00e9m\u00e8res in situ.",
    "individuel", 45, tous,
    [122,240,245],  # Representation de la nature, Estime de soi, Introspection
    [15,1],
    {"Cycle 1":[523,526,530,572],
     "Cycle 2":[617,618,620,573,575],
     "Cycle 3":[758,759,762,674,755]})

# 758 - Loup garou nature
add(758, IE,
    "Version naturaliste du jeu des loups-garous : les participants incarnent des r\u00f4les inspir\u00e9s de la for\u00eat (loup, louve, louveteaux, braconnier, herboriste, naturaliste, randonneur). La nuit, les personnages agissent en secret ; le jour, les villageois d\u00e9lib\u00e8rent et votent pour \u00e9liminer un suspect.",
    "D\u00e9velopper la strat\u00e9gie, la communication et comprendre les relations pr\u00e9dateur-proie \u00e0 travers un jeu de r\u00f4le immersif.",
    "grand groupe", 30, tous,
    [37,190,126],  # Ethologie, Relations ecologiques, Vivre ensemble
    [16,6],
    {"Cycle 2":[638,639,643,644,645,648],
     "Cycle 3":[749,750,754,756,757,806]},
    meteo={"nuit":1})  # version bougies la nuit est un plus

# 354 - Masque naturel sur tige
add(354, IE,
    "Les participants collectent une grande feuille (bardane, ch\u00e2taignier) comme base et y fixent des \u00e9l\u00e9ments naturels d\u00e9coratifs (fleurs, mousses, p\u00e9tales, herbes) pour cr\u00e9er un masque \u00e9ph\u00e9m\u00e8re tenu devant le visage \u00e0 l\u2019aide d\u2019une tige.",
    "D\u00e9velopper la cr\u00e9ativit\u00e9 et le sens esth\u00e9tique en explorant les formes et textures du vivant pour fabriquer un accessoire symbolique et \u00e9ph\u00e9m\u00e8re.",
    "individuel", 40, [4,5,6,7,8,9],  # printemps-ete
    [122,42,138],  # Representation de la nature, Regne vegetal, Tactile
    [15,3],
    {"Cycle 1":[523,526,530,564],
     "Cycle 2":[617,618,620,648],
     "Cycle 3":[758,759,760,784]})

# 215 - Montrer la gelifraction avec un oeuf
add(215, IE,
    "Les participants placent un \u0153uf dans un sachet herm\u00e9tique et le mettent au cong\u00e9lateur. Le lendemain, ils observent que l\u2019\u0153uf a \u00e9clat\u00e9 sous l\u2019effet de la dilatation. Une discussion relie ce ph\u00e9nom\u00e8ne \u00e0 la g\u00e9lifraction des roches : l\u2019eau s\u2019infiltrant dans les fissures g\u00e8le et \u00e9clate la roche.",
    "Comprendre le m\u00e9canisme de la g\u00e9lifraction en exp\u00e9rimentant la dilatation de l\u2019eau lors de la cong\u00e9lation.",
    "petit groupe", 20, [10,11,12,1,2,3],  # hiver
    [80,81,84],  # Relief, Erosion, Climat
    [6,4],
    {"Cycle 2":[646,647,648,665],
     # 646 etats matiere, 647 changement etat eau, 648 caracteristiques vivant, 665 comparer/estimer mesurer
     "Cycle 3":[774,775,804,805,802]})
     # 774 decrire matiere, 775 diversite matiere, 804 differencier meteo/climat, 805 rechauffement climatique, 802 activite Terre

# 757 - Memory oiseaux
add(757, I,
    "Jeu de m\u00e9mory avec des cartes repr\u00e9sentant des oiseaux communs : chaque paire associe le nom de l\u2019oiseau \u00e0 son illustration. Deux versions de difficult\u00e9 sont disponibles (avec ou sans noms). Les participants retournent les cartes face cach\u00e9e et cherchent les paires.",
    "Apprendre \u00e0 reconna\u00eetre les oiseaux communs et d\u00e9velopper la m\u00e9moire visuelle et la concentration.",
    "petit groupe", 25, tous,
    [20,3],  # Groupes animaux, Taxonomie
    [4,3],   # Connaitre nature, Observer nature
    {"Cycle 1":[564,565,533,534,498],
     "Cycle 2":[648,574,604,623],
     "Cycle 3":[784,785,714]})

# 755 - Memory petite faune
add(755, I,
    "Jeu de m\u00e9mory avec des cartes repr\u00e9sentant la petite faune du quotidien (insectes, araign\u00e9es, mollusques, myriapodes). Chaque paire associe deux illustrations identiques. L\u2019activit\u00e9 peut s\u2019enrichir d\u2019une phase d\u2019identification et de discussion sur chaque animal d\u00e9couvert.",
    "Apprendre \u00e0 reconna\u00eetre la petite faune locale souvent m\u00e9connue et favoriser un regard bienveillant envers les invert\u00e9br\u00e9s.",
    "petit groupe", 25, tous,
    [22,23,20],  # Insectes, Arachnides, Groupes animaux
    [4,3],
    {"Cycle 1":[564,565,533,534,472],
     # 472 prendre conscience richesse biodiversite
     "Cycle 2":[648,574,573,575,604],
     "Cycle 3":[784,785,674,714]})

db.commit()
db.close()
print("Lot 7 termine.")
