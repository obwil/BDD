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

# 1241 - Observer la dispersion explosive des plantes
add(1241, E,
    "Les participants cherchent et observent des plantes \u00e0 dispersion explosive (balsamine, cardamine, g\u00e9ranium herbe-\u00e0-robert, gen\u00eats). Ils d\u00e9clenchent l\u2019explosion en touchant d\u00e9licatement les capsules m\u00fbres et discutent de cette strat\u00e9gie de reproduction.",
    "Comprendre la dissimination explosive comme strat\u00e9gie de reproduction v\u00e9g\u00e9tale et observer in situ le m\u00e9canisme.",
    "petit groupe", 30, [6,7,8,9],  # ete-automne
    [17,63,49],  # Reproduction, Comportement vegetal, Groupes vegetaux
    [3,6],
    {"Cycle 2":[648,581,574,573],
     "Cycle 3":[784,788,806,674,695]})

# 1243 - Observer le fer dans les cereales
add(1243, I,
    "Les participants testent la pr\u00e9sence de fer dans des c\u00e9r\u00e9ales \u00e0 l\u2019aide d\u2019un aimant : d\u2019abord sur des flocons secs, puis flottant dans l\u2019eau, puis apr\u00e8s avoir mixe les c\u00e9r\u00e9ales avec de l\u2019eau pour extraire les particules de fer \u00e9l\u00e9mentaire visibles \u00e0 la paroi du gobelet.",
    "Visualiser la pr\u00e9sence de fer dans les aliments par ses propri\u00e9t\u00e9s magn\u00e9tiques et relier ce nutriment \u00e0 son r\u00f4le dans l\u2019organisme.",
    "petit groupe", 40, tous,
    [248,235],  # Alimentation saine, Respiration cellulaire (fer = hemoglobine)
    [6,4],
    {"Cycle 2":[646,648,649,582,592],
     # 646 etats matiere, 648 car vivant, 649 comportements favorables sante, 582 equilibre alimentaire, 592 liens alimentation/ressources
     "Cycle 3":[774,775,786,787,680]})
     # 774 decrire matiere, 775 diversite matiere, 786 role aliments organisme, 787 technologies transformer aliments, 680 connaissance scientifique vs opinion alimentation

# 193 - Observer le herisson
add(193, E,
    "Les participants apprennent \u00e0 d\u00e9tecter la pr\u00e9sence d\u2019un h\u00e9risson dans un jardin ou un milieu naturel : traces, crottes, empreintes, nids d\u2019hibernation, indices de nourrissage. Une phase de d\u00e9couverte de la biologie du h\u00e9risson (alimentation, hibernation, d\u00e9fense) compl\u00e8te l\u2019observation.",
    "D\u00e9couvrir la biologie et les comportements du h\u00e9risson, apprendre \u00e0 d\u00e9tecter sa pr\u00e9sence par les traces et indices.",
    "petit groupe", 40, tous,
    [37,20,37],  # Ethologie, Groupes animaux
    [3,4],
    {"Cycle 1":[564,565,572],
     "Cycle 2":[648,574,573,575,578],
     "Cycle 3":[784,785,806,674,808]})

# 1244 - Observer les differents types de champignons
add(1244, E,
    "En for\u00eat, les participants cherchent des champignons et observent leur substrat pour distinguer les mycorhiziens (base propre, li\u00e9s aux racines des arbres) des saprotrophes de liti\u00e8re (d\u00e9bris attach\u00e9s au pied) et des saprotrophes du bois (sur troncs ou branches mortes). Ils classent leurs observations et discutent du r\u00f4le de chaque type dans l\u2019\u00e9cosyst\u00e8me.",
    "Distinguer les diff\u00e9rents modes de vie des champignons et comprendre leur r\u00f4le essentiel dans les \u00e9cosyst\u00e8mes forestiers.",
    "petit groupe", 60, [8,9,10,11],  # automne
    [65,71,73,161],  # Champignons, Mycorhizes, Saprophytes, Ecologie
    [3,6],
    {"Cycle 2":[648,574,573,575,578],
     "Cycle 3":[784,785,806,807,674]})

# 1240 - Observer l interieur d un oeuf
add(1240, I,
    "Les participants plongent un \u0153uf cru dans du vinaigre pendant 1 \u00e0 2 jours. Le vinaigre dissout la coquille calcaire et r\u00e9v\u00e8le la membrane int\u00e9rieure, rendant l\u2019\u0153uf translucide. On peut alors observer le jaune \u00e0 travers la membrane et discuter du d\u00e9veloppement de l\u2019embryon.",
    "Comprendre la composition de la coquille d\u2019\u0153uf et observer la structure interne de l\u2019\u0153uf gr\u00e2ce \u00e0 une r\u00e9action chimique simple.",
    "petit groupe", 30, tous,
    [233,17,130],  # Reactions chimiques, Reproduction, Physiologie
    [6,3],
    {"Cycle 2":[646,647,648,649,581],
     "Cycle 3":[774,775,788,789,784]})

db.commit()
db.close()
print("Lot 8 termine.")
