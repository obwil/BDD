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

# 455 - Observer l osmose avec un oeuf
add(455, I,
    "Les participants dissolvent la coquille d\u2019un \u0153uf cru dans le vinaigre (24-48h), obtenant un \u0153uf translucide. Ils testent ensuite l\u2019osmose en pla\u00e7ant l\u2019\u0153uf dans de l\u2019eau pure (il gonfle) puis dans du sirop concentr\u00e9 (il r\u00e9tr\u00e9cit), rendant visible le passage de l\u2019eau \u00e0 travers la membrane semi-perm\u00e9able.",
    "Comprendre le m\u00e9canisme de l\u2019osmose et la notion de membrane semi-perm\u00e9able \u00e0 travers une exp\u00e9rience \u00e9tal\u00e9e sur plusieurs jours.",
    "petit groupe", 30, tous,
    [233,130,235],  # Reactions chimiques, Physiologie, Respiration cellulaire
    [6,4],
    {"Cycle 2":[646,647,648,649],
     "Cycle 3":[774,775,788,784,803]})
     # 803 decrire conditions vie terrestre

# 1245 - Orgue eolien en bambous
add(1245, E,
    "Les participants fabriquent un orgue \u00e9olien en taillant des tubes de bambou de longueurs et diam\u00e8tres diff\u00e9rents avec des biseaux \u00e0 l\u2019ouverture. Assembl\u00e9s sur un support et orient\u00e9s face au vent, les tubes produisent des sons graves et fl\u00fbt\u00e9s dont la hauteur d\u00e9pend de la longueur du tube.",
    "Comprendre le principe acoustique de r\u00e9sonance dans un tube et cr\u00e9er une installation sonore activ\u00e9e par le vent.",
    "petit groupe", 90, tous,
    [120,60,134],  # Musique du monde, Tige creuse, Audition
    [15,18],
    {"Cycle 2":[622,623,624,650,619],
     "Cycle 3":[725,726,727,791,797]},
    meteo={"vent":1})  # necessite du vent pour fonctionner

# 1246 - Panier en feuille
add(1246, IE,
    "Les participants collectent des feuilles longues et souples, puis les tressent selon une technique de vannerie simple pour r\u00e9aliser un petit panier avec anse. La base carr\u00e9e est form\u00e9e en croisant les bandes, les parois mont\u00e9es en tressant, et les bords finis en rabattant les extr\u00e9mit\u00e9s.",
    "Initier \u00e0 la vannerie v\u00e9g\u00e9tale, d\u00e9velopper la dext\u00e9rit\u00e9 fine et d\u00e9couvrir les propri\u00e9t\u00e9s des mat\u00e9riaux v\u00e9g\u00e9taux.",
    "individuel", 50, tous,
    [128,49],  # Traditions, Groupes vegetaux
    [15,5],
    {"Cycle 1":[523,526,568,564],
     "Cycle 2":[617,618,619,648],
     "Cycle 3":[758,759,762,784]})

# 220 - Peindre des oeufs (oeufs camoufles)
add(220, E,
    "Les enfants observent des images d\u2019\u0153ufs d\u2019oiseaux nichant au sol (camouflage de couleur et de motif). Puis ils peignent des \u0153ufs durs pour les camoufler au mieux dans un environnement choisi, imitant les strat\u00e9gies r\u00e9elles des oiseaux. Les \u0153ufs camoufl\u00e9s sont ensuite cach\u00e9s et recherch\u00e9s.",
    "Comprendre les strat\u00e9gies de camouflage des \u0153ufs d\u2019oiseaux nicheurs et explorer l\u2019adaptation au milieu.",
    "individuel", 50, [3,4,5,6],  # printemps
    [37,158,20],  # Ethologie, Adaptation, Groupes animaux
    [3,6],
    {"Cycle 1":[523,524,564,565,572],
     "Cycle 2":[617,618,648,574,573],
     "Cycle 3":[784,785,758,806,157]})
     # 157 selection naturelle

# 583 - Photolangage - eau
add(583, I,
    "Les participants choisissent parmi 27 photographies sur le th\u00e8me de l\u2019eau (paysages, usages, \u00e9tats, milieux) celle(s) qui repr\u00e9sentent le mieux l\u2019eau pour eux. Les choix sont partag\u00e9s et discut\u00e9s en groupe pour explorer repr\u00e9sentations, \u00e9motions et connaissances.",
    "Favoriser l\u2019expression orale et partager les repr\u00e9sentations autour de l\u2019eau, en ouverture ou conclusion d\u2019une s\u00e9quence sur le cycle de l\u2019eau.",
    "grand groupe", 30, tous,
    [221,163,222],  # L eau, Cycle eau, Etats eau
    [6,2],
    {"Cycle 1":[482,483,484,501,530],
     "Cycle 2":[586,587,604,607,639],
     "Cycle 3":[684,686,691,714,717]})

db.commit()
db.close()
print("Lot 9 termine.")
