import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
db = sqlite3.connect(r"C:\Users\moina\Dropbox\Outils\BDD activit" + chr(233) + r"s\_OUTIL\activites.db")
cur = db.cursor()
cur.execute("SELECT id, nom FROM cycle")
cycles = {r[1]: r[0] for r in cur.fetchall()}

def set_activite(aid, lieu, desc, obj_txt, fmt, duree, mois, themes, objectifs, cycles_attendus, meteo=None):
    mois_vals = [1 if (i+1) in mois else 0 for i in range(12)]
    m = meteo or {}
    cur.execute("""UPDATE activite SET lieu=?,description=?,objectif_texte=?,format_groupe=?,duree_min=?,
        mois_jan=?,mois_fev=?,mois_mar=?,mois_avr=?,mois_mai=?,mois_jun=?,
        mois_jul=?,mois_aou=?,mois_sep=?,mois_oct=?,mois_nov=?,mois_dec=?,
        meteo_soleil=?,meteo_nuage=?,meteo_pluie=?,meteo_vent=?,meteo_nuit=?
        WHERE id=?""",
        (lieu,desc,obj_txt,fmt,duree,*mois_vals,
         m.get("soleil",0),m.get("nuage",0),m.get("pluie",0),m.get("vent",0),m.get("nuit",0),
         aid))
    for tid in themes:
        cur.execute("SELECT 1 FROM activite_thematique WHERE activite_id=? AND thematique_id=?", (aid,tid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_thematique(activite_id,thematique_id) VALUES(?,?)", (aid,tid))
    for oid in objectifs:
        cur.execute("SELECT 1 FROM activite_objectif WHERE activite_id=? AND objectif_id=?", (aid,oid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_objectif(activite_id,objectif_id) VALUES(?,?)", (aid,oid))
    for cycle_nom, attendu_ids in cycles_attendus.items():
        cid = cycles[cycle_nom]
        cur.execute("SELECT 1 FROM activite_cycle WHERE activite_id=? AND cycle_id=?", (aid,cid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_cycle(activite_id,cycle_id) VALUES(?,?)", (aid,cid))
        cur.execute("SELECT 1 FROM activite_cycle_analysee WHERE activite_id=? AND cycle_id=?", (aid,cid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_cycle_analysee(activite_id,cycle_id,statut) VALUES(?,?,'ok')", (aid,cid))
        else:
            cur.execute("UPDATE activite_cycle_analysee SET statut='ok' WHERE activite_id=? AND cycle_id=?", (aid,cid))
        for att_id in attendu_ids:
            cur.execute("SELECT 1 FROM activite_attendu WHERE activite_id=? AND attendu_id=?", (aid,att_id))
            if not cur.fetchone():
                cur.execute("INSERT INTO activite_attendu(activite_id,attendu_id) VALUES(?,?)", (aid,att_id))
    print(f"ID {aid} OK")

tous = list(range(1,13))

# 430 - Conte sur le coeur
set_activite(430,
    "Ext" + chr(233) + "rieur",
    "L\u2019animateur lit ou r" + chr(233) + "cite un po" + chr(232) + "me-conte sur les " + chr(233) + "tats du c" + chr(153) + "ur (\u00ab\u00a0mon c" + chr(153) + "ur est une fen" + chr(234) + "tre\u00a0\u00bb, \u00ab\u00a0un toboggan\u00a0\u00bb, \u00ab\u00a0une flaque\u00a0\u00bb...). Le texte ouvre un espace de parole sur les " + chr(233) + "motions, la vuln" + chr(233) + "rabilit" + chr(233) + " et la r" + chr(233) + "silience, en s\u2019appuyant sur des m" + chr(233) + "taphores naturelles.",
    "Ouvrir un espace d\u2019expression " + chr(233) + "motionnelle en s\u2019appuyant sur un texte po" + chr(233) + "tique utilisant des m" + chr(233) + "taphores de la nature.",
    "grand groupe", 20, tous,
    [249, 245, 122],   # Emotions, Introspection, Representation de la nature
    [2, 17],            # Ressentir nature, Imaginer
    {
        "Cycle 1": [501, 502, 530, 531],
        # 501 usages langue orale, 502 comptines/poesies memorisees, 530 decrire ressenti, 531 proposer solutions avec voix/corps
        "Cycle 2": [604, 606, 625, 639, 645],
        # 604 ecoute, 606 raconter/decrire, 625 sensibilite esprit critique, 639 partager emotions, 645 ecouter/argumenter
        "Cycle 3": [714, 717, 728, 750, 756]
        # 714 ecouter recit, 717 echanges constructifs, 728 sensibilite diversite, 750 partager emotions vocab adapte, 756 reflexion critique
    })

# 927 - Course des chenilles
set_activite(927,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants fabriquent une chenille en papier pli" + chr(233) + " en accord" + chr(233) + "on, la d" + chr(233) + "corent, puis participent " + chr(224) + " une course en soufflant sur leur cr" + chr(233) + "ation " + chr(224) + " l\u2019aide d\u2019une paille pour la faire avancer jusqu\u2019" + chr(224) + " la ligne d\u2019arriv" + chr(233) + "e.",
    "Explorer le th" + chr(232) + "me des insectes " + chr(224) + " travers une activit" + chr(233) + " de fabrication ludique d" + chr(233) + "veloppant la d" + chr(233) + "xt" + chr(233) + "rit" + chr(233) + " et la coordination.",
    "grand groupe", 35, tous,
    [22, 37],    # Insectes, Ethologie
    [15, 16],    # Creer avec la nature, Jouer dans la nature
    {
        "Cycle 1": [523, 524, 525, 568, 564],
        # 523 outils/mediums, 524 dessiner, 525 reproduire graphismes, 568 outils materiaux, 564 etapes developpement vivant
        "Cycle 2": [617, 618, 648, 626, 634],
        # 617 productions plastiques, 618 reponses inventives, 648 caracteristiques vivant, 626 courir/sauter/lancer, 634 affrontement regles
        "Cycle 3": [758, 784, 785]
        # 758 productions plastiques, 784 richesse vivant, 785 classer organismes
    })

# 505 - Creer de l art avec des ombres
set_activite(505,
    "Ext" + chr(233) + "rieur",
    "Les participants collectent des objets naturels (branches, feuilles, pierres, fleurs) et les posent sur du papier en plein soleil. Ils tracent le contour des ombres projet" + chr(233) + "es pour cr" + chr(233) + "er une composition artistique. L\u2019activit" + chr(233) + " peut se renouveler " + chr(224) + " diff" + chr(233) + "rents moments de la journ" + chr(233) + "e pour observer les variations d\u2019ombres.",
    "Explorer les ph" + chr(233) + "nom" + chr(232) + "nes d\u2019ombre et de lumi" + chr(232) + "re " + chr(224) + " travers une d" + chr(233) + "marche artistique utilisant des " + chr(233) + "l" + chr(233) + "ments naturels.",
    "individuel", 40, tous,
    [229, 122],   # Lumiere, Representation de la nature
    [15, 3],      # Creer avec la nature, Observer la nature
    {
        "Cycle 1": [523, 524, 526, 530],
        # 523 outils/mediums, 524 dessiner, 526 compositions plastiques materiaux, 530 decrire ressenti
        "Cycle 2": [617, 618, 620, 621],
        # 617 productions plastiques, 618 reponses inventives, 620 s exprimer sur sa production, 621 comparer oeuvres
        "Cycle 3": [758, 759, 760, 781]
        # 758 productions plastiques, 759 justifier choix plastiques, 760 decrire productions, 781 interpreter formation ombres
    },
    meteo={"soleil": 1})

# 380 - Creer des pinceaux naturels
set_activite(380,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants collectent des " + chr(233) + "l" + chr(233) + "ments naturels (feuilles, herbes, mousses, fleurs, c" + chr(244) + "nes, plumes) et les attachent " + chr(224) + " une branche avec de la ficelle pour fabriquer des pinceaux v" + chr(233) + "g" + chr(233) + "taux. Ils s\u2019en servent ensuite pour peindre, chaque mat" + chr(233) + "riau laissant une texture et une empreinte uniques.",
    "D" + chr(233) + "couvrir les textures et formes du vivant en fabricant des outils artistiques naturels et en explorant leurs effets plastiques.",
    "individuel", 50, tous,
    [122, 138],   # Representation de la nature, Tactile
    [15, 3],      # Creer avec la nature, Observer la nature
    {
        "Cycle 1": [523, 524, 526, 568, 530],
        # 523 outils/mediums, 524 dessiner, 526 compositions plastiques, 568 outils materiaux, 530 decrire ressenti
        "Cycle 2": [617, 618, 619, 620, 648],
        # 617 productions plastiques, 618 reponses inventives, 619 cooperer, 620 s exprimer, 648 caracteristiques vivant
        "Cycle 3": [758, 759, 760, 762]
        # 758 productions plastiques, 759 justifier choix, 760 decrire productions, 762 projet artistique
    })

# 847 - Creer des pochoirs-cadres nature
set_activite(847,
    "Ext" + chr(233) + "rieur",
    "Les participants d" + chr(233) + "coupent des formes dans du carton pour cr" + chr(233) + "er des cadres ou pochoirs. Ils les posent sur des " + chr(233) + "l" + chr(233) + "ments naturels pour \u00ab\u00a0encadrer\u00a0\u00bb des sc" + chr(232) + "nes de nature, jouent sur les perspectives en les tenant devant un paysage, ou y ins" + chr(232) + "rent des fleurs et tiges pour cr" + chr(233) + "er un bouquet encadr" + chr(233) + ".",
    "D" + chr(233) + "velopper le regard artistique et l\u2019observation de la nature en jouant sur le cadrage, la composition et la mise en sc" + chr(232) + "ne d\u2019" + chr(233) + "l" + chr(233) + "ments du vivant.",
    "individuel", 40, tous,
    [122, 43],    # Representation de la nature, Strates
    [15, 3],      # Creer avec la nature, Observer la nature
    {
        "Cycle 1": [523, 524, 530, 558, 559],
        # 523 outils/mediums, 524 dessiner, 530 decrire ressenti, 558 situer objets, 559 se situer par rapport aux autres
        "Cycle 2": [617, 618, 620, 621, 648],
        # 617 productions plastiques, 618 reponses inventives, 620 s exprimer, 621 comparer oeuvres, 648 caracteristiques vivant
        "Cycle 3": [758, 759, 760, 761, 762]
        # 758 productions plastiques, 759 justifier choix, 760 decrire, 761 caracteristiques inscription oeuvre, 762 projet artistique
    })

db.commit()
db.close()
print("Lot 3 termine.")
