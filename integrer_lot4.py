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
         m.get("soleil",0),m.get("nuage",0),m.get("pluie",0),m.get("vent",0),m.get("nuit",0),aid))
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

# 929 - Creer un tableau avec des elements de la nature
set_activite(929,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants collectent des feuilles d\u2019arbres de formes et couleurs vari" + chr(233) + "es, puis les int" + chr(232) + "grent " + chr(224) + " un tableau artistique en les collant sur un support et en compl" + chr(233) + "tant la composition au dessin : personnages, papillons, d" + chr(233) + "cors. Chaque feuille devient corps, aile ou " + chr(233) + "l" + chr(233) + "ment de paysage.",
    "D" + chr(233) + "velopper la cr" + chr(233) + "ativit" + chr(233) + " et l\u2019imaginaire en int" + chr(233) + "grant des formes v" + chr(233) + "g" + chr(233) + "tales r" + chr(233) + "elles dans une composition artistique.",
    "individuel", 90, tous,
    [122, 42],    # Representation de la nature, Regne vegetal
    [15, 3],      # Creer avec la nature, Observer la nature
    {
        "Cycle 1": [523, 524, 525, 526, 530],
        "Cycle 2": [617, 618, 619, 620, 648],
        "Cycle 3": [758, 759, 760, 762, 784]
    })

# 930 - Creer une carte des ecosystemes (microhabitats)
set_activite(930,
    "Int" + chr(233) + "rieur",
    "Les participants colorient, d" + chr(233) + "coupent et assemblent une carte interactive pliable repr" + chr(233) + "sentant diff" + chr(233) + "rents microhabitats (sous une pierre, au bord de l\u2019eau, dans un arbre...). Ils associent chaque animal " + chr(224) + " son microhabitat en le collant dans la section correspondante, puis pr" + chr(233) + "sentent leurs choix au groupe.",
    "D" + chr(233) + "couvrir la notion de microhabitat et comprendre les liens entre les animaux et leur milieu de vie.",
    "individuel", 55, tous,
    [176, 190, 37],   # Ecosystemes, Relations ecologiques, Ethologie
    [4, 6],            # Connaitre nature, Comprendre nature
    {
        "Cycle 1": [564, 565, 568, 558, 561],
        # 564 etapes developpement vivant, 565 besoins animaux/vegetaux, 568 outils/materiaux, 558 situer objets espace, 561 representation plane
        "Cycle 2": [648, 650, 658, 653, 617],
        # 648 caracteristiques vivant, 650 fonctionnement objets fabriques, 658 interactions mode de vie/environnement, 653 se reperer espace, 617 productions plastiques
        "Cycle 3": [784, 806, 808, 785, 760]
        # 784 richesse vivant, 806 decrire ecosysteme, 808 consequences action humaine, 785 classer organismes, 760 decrire productions
    })

# 932 - Creer une guirlande de l automne
set_activite(932,
    "Ext" + chr(233) + "rieur",
    "Les participants cueillent des feuilles mortes aux couleurs d\u2019automne et les assemblent en guirlande en les fixant avec des \u00ab\u00a0agrafes\u00a0\u00bb de fines brindilles s" + chr(232) + "ches. Ils jouent sur les formes, couleurs et dip" + chr(244) + "les pour cr" + chr(233) + "er des guirlandes lin" + chr(233) + "aires ou des rosettes d" + chr(233) + "coratives.",
    "Observer la diversit" + chr(233) + " des feuilles d\u2019automne et d" + chr(233) + "velopper la dext" + chr(233) + "rit" + chr(233) + " en r" + chr(233) + "alisant une cr" + chr(233) + "ation artistique uniquement " + chr(224) + " partir de mat" + chr(233) + "riaux naturels.",
    "individuel", 60, [9, 10, 11],   # sept-oct-nov
    [122, 42, 43],    # Representation de la nature, Regne vegetal, Strates
    [15, 3],           # Creer avec la nature, Observer la nature
    {
        "Cycle 1": [523, 526, 530, 564],
        "Cycle 2": [617, 618, 620, 648],
        "Cycle 3": [758, 759, 760, 784]
    })

# 518 - Creer une maquette des abris des animaux
set_activite(518,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants construisent une maquette en coupe repr" + chr(233) + "sentant les diff" + chr(233) + "rents abris des animaux dans la nature : terriers souterrains (renard, blaireau, fourmis), cavit" + chr(233) + "s dans les arbres (" + chr(233) + "cureuil, chouette), abris sous pierres ou feuilles. La maquette est construite dans un bac avec terre, mousse et " + chr(233) + "l" + chr(233) + "ments naturels.",
    "D" + chr(233) + "couvrir la diversit" + chr(233) + " des habitats animaux et comprendre les liens entre chaque animal et son environnement.",
    "petit groupe", 60, tous,
    [37, 20, 176],    # Ethologie, Groupes animaux, Ecosystemes
    [4, 18],           # Connaitre nature, Construire dans la nature
    {
        "Cycle 1": [564, 565, 568, 569, 558],
        # 564 etapes developpement, 565 besoins animaux, 568 outils/materiaux, 569 construire maquettes, 558 situer objets
        "Cycle 2": [648, 650, 658, 617, 653],
        # 648 caracteristiques vivant, 650 fonctionnement objets, 658 interactions mode de vie, 617 productions plastiques, 653 se reperer espace
        "Cycle 3": [784, 806, 785, 758, 808]
        # 784 richesse vivant, 806 decrire ecosysteme, 785 classer organismes, 758 productions plastiques, 808 consequences action humaine
    })

# 933 - Creer une etoile / coeur vegetal
set_activite(933,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants fabriquent une " + chr(233) + "toile " + chr(224) + " cinq branches ou un c" + chr(153) + "ur en tressant et entrecroisant des rameaux souples (osier, saule, cornouiller). Les branches sont crois" + chr(233) + "es et maintenues par enroulement de ficelle, raphia ou laine color" + chr(233) + "e. Une variante consiste " + chr(224) + " tisser de la laine entre les branches pour remplir l\u2019int" + chr(233) + "rieur.",
    "Initier au tressage et " + chr(224) + " la vannerie v" + chr(233) + "g" + chr(233) + "tale, d" + chr(233) + "couvrir la flexibilit" + chr(233) + " de certains v" + chr(233) + "g" + chr(233) + "taux et d" + chr(233) + "velopper la motricit" + chr(233) + " fine.",
    "individuel", 45, [1,2,3,4,10,11,12],   # automne/hiver/printemps (taille)
    [128, 63],    # Traditions, Comportement vegetal
    [15, 5],      # Creer avec la nature, Decouvrir la nature
    {
        "Cycle 1": [523, 526, 568, 564],
        "Cycle 2": [617, 618, 619, 648],
        "Cycle 3": [758, 759, 762, 784]
    })

db.commit()
db.close()
print("Lot 4 termine.")
