import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
db = sqlite3.connect(r"C:\Users\moina\Dropbox\Outils\BDD activit" + chr(233) + r"s\_OUTIL\activites.db")
cur = db.cursor()
cur.execute("SELECT id, nom FROM cycle")
cycles = {r[1]: r[0] for r in cur.fetchall()}

def add(aid, lieu, desc, obj_txt, fmt, duree, mois, themes, objectifs, ca):
    mois_vals = [1 if (i+1) in mois else 0 for i in range(12)]
    cur.execute("""UPDATE activite SET lieu=?,description=?,objectif_texte=?,format_groupe=?,duree_min=?,
        mois_jan=?,mois_fev=?,mois_mar=?,mois_avr=?,mois_mai=?,mois_jun=?,
        mois_jul=?,mois_aou=?,mois_sep=?,mois_oct=?,mois_nov=?,mois_dec=?
        WHERE id=?""", (lieu,desc,obj_txt,fmt,duree,*mois_vals,aid))
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

add(1227, IE,
    "Jeu de plateau strat\u00e9gique \u00e0 deux joueurs sur un r\u00e9seau de points reli\u00e9s par des chemins. L\u2019un joue le poursuivant, l\u2019autre le poursuivi ; chacun avance d\u2019un point par tour. Le poursuivant gagne en atteignant le point du poursuivi. Peut \u00e9galement se jouer en grandeur nature dans la nature.",
    "D\u00e9velopper la strat\u00e9gie, l\u2019anticipation et la logique spatiale.",
    "binome", 20, tous, [125,161], [16,12],
    {"Cycle 1":[558,559,560,522,535], "Cycle 2":[634,636,637,668,643], "Cycle 3":[744,745,746,747,748]})

add(1228, E,
    "Les participants fabriquent des \u00ab\u00a0plioirs\u00a0\u00bb en pliant des cartes \u00e0 jouer recycl\u00e9es en plusieurs \u00e9paisseurs, puis s\u2019affrontent en lan\u00e7ant leurs plioirs pour retourner ceux des adversaires. Le joueur qui collecte le plus de plioirs retourne gagne.",
    "D\u00e9velopper l\u2019adresse et la coordination tout en jouant avec du mat\u00e9riel recycl\u00e9.",
    "grand groupe", 35, tous, [125,117], [16],
    {"Cycle 1":[517,518,519,522,568], "Cycle 2":[626,628,629,634,636], "Cycle 3":[734,744,746,747,748]})

add(258, I,
    "Les participants observent des photographies de milieux naturels dans lesquelles des animaux sont camoufl\u00e9s. Le d\u00e9fi consiste \u00e0 rep\u00e9rer tous les animaux cach\u00e9s. L\u2019activit\u00e9 est enrichie par une discussion sur les strat\u00e9gies de camouflage (mim\u00e9tisme chromatique, de forme, comportement immobile).",
    "Comprendre les m\u00e9canismes du camouflage animal, d\u00e9velopper l\u2019observation fine et d\u00e9couvrir la biodiversit\u00e9 cach\u00e9e dans les milieux naturels.",
    "individuel", 30, tous, [37,158,20], [3,4],
    {"Cycle 1":[564,565,570,499,500], "Cycle 2":[648,574,601,604,607], "Cycle 3":[784,785,806,714,717]})

add(611, I,
    "Les enfants re\u00e7oivent des images d\u2019animaux et doivent les associer au type de for\u00eat qui leur correspond ainsi qu\u2019\u00e0 la bonne taille de for\u00eat. L\u2019activit\u00e9 permet de comprendre les besoins sp\u00e9cifiques de chaque esp\u00e8ce et ce qu\u2019on peut trouver dans les for\u00eats de proximit\u00e9.",
    "Comprendre les besoins des animaux forestiers et les relations entre les esp\u00e8ces et leur habitat.",
    "petit groupe", 25, tous, [37,20,167], [4,6],
    {"Cycle 1":[564,565,558,563,500], "Cycle 2":[648,658,574,653,607], "Cycle 3":[784,806,808,785,672]})

add(469, IE,
    "L\u2019animateur raconte l\u2019histoire de l\u2019eau \u00e0 travers les \u00e2ges \u00e0 l\u2019aide d\u2019un kamishibai (th\u00e9\u00e2tre d\u2019images japonais). Le r\u00e9cit retrace les diff\u00e9rentes formes et usages de l\u2019eau depuis les origines, invitant les enfants \u00e0 r\u00e9fl\u00e9chir sur l\u2019importance de cette ressource.",
    "D\u00e9couvrir l\u2019histoire et les usages de l\u2019eau \u00e0 travers les civilisations, et sensibiliser \u00e0 sa valeur comme bien commun.",
    "grand groupe", 30, tous, [221,163], [6,1],
    {"Cycle 1":[482,483,484,501,555], "Cycle 2":[586,587,588,589,604,656], "Cycle 3":[684,686,687,691,692,714]})

db.commit()
db.close()
print("Lot 6 termine.")
