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

# 934 - Cueillir des orties
set_activite(934,
    "Ext" + chr(233) + "rieur",
    "Les participants apprennent " + chr(224) + " reconna" + chr(238) + "tre et " + chr(224) + " cueillir des orties sans se piquer, en utilisant la technique de pincement ferme dans le sens de la tige. L\u2019activit" + chr(233) + " s\u2019accompagne d\u2019explications sur le m" + chr(233) + "canisme des poils urticants et sur les usages de l\u2019ortie (alimentaire, textile, m" + chr(233) + "dicinale).",
    "Surmonter la peur d\u2019une plante mal-aim" + chr(233) + "e, comprendre le m" + chr(233) + "canisme d\u2019urticance et d" + chr(233) + "couvrir les multiples usages de l\u2019ortie.",
    "petit groupe", 30, [3,4,5,6,7,8,9],  # printemps-ete
    [49, 130, 282],   # Groupes vegetaux, Physiologie, Gestion durable ressources
    [5, 4],            # Decouvrir nature, Connaitre nature
    {
        "Cycle 1": [564, 565, 572, 567],
        # 564 etapes developpement vivant, 565 besoins animaux/vegetaux, 572 attitude responsable protection vivant, 567 hygiene/vie saine
        "Cycle 2": [648, 573, 575, 578, 592],
        # 648 caracteristiques vivant, 573 sensible biodiversite, 575 biodiversite bien commun, 578 ecogestes, 592 liens alimentation/besoins/ressources
        "Cycle 3": [784, 674, 677, 786, 695]
        # 784 richesse vivant, 674 biodiversite bien commun, 677 produits locaux/sante, 786 role aliments organisme, 695 demarche investigation gestion ressources
    })

# 937 - Decouvrir le silex
set_activite(937,
    "Ext" + chr(233) + "rieur",
    "Les participants d" + chr(233) + "couvrent le silex : sa formation g" + chr(233) + "ologique, comment le reconna" + chr(238) + "tre (aspect, texture, cassure concho" + chr(239) + "dale), et ses usages pr" + chr(233) + "historiques. Une d" + chr(233) + "monstration de taille permet de produire des " + chr(233) + "clats tranchants et d\u2019initier " + chr(224) + " la fabrication d\u2019outils primitifs. La percussion de deux silex peut " + chr(233) + "galement produire des " + chr(233) + "tincelles.",
    "Comprendre l\u2019histoire de la pr" + chr(233) + "histoire " + chr(224) + " travers la ma" + chr(238) + "trise du silex, d" + chr(233) + "velopper l\u2019observation min" + chr(233) + "ralogique et exp" + chr(233) + "rimenter des techniques ancestrales.",
    "petit groupe", 60, tous,
    [75, 76, 121],    # Mineraux, Roches, Patrimoine
    [4, 11],           # Connaitre nature, Evoluer dans la nature
    {
        "Cycle 2": [646, 648, 657, 650, 647],
        # 646 trois etats matiere, 648 caracteristiques vivant, 657 modes de vie, 650 fonctionnement objets, 647 changement etat eau
        "Cycle 3": [774, 775, 776, 768, 769, 791]
        # 774 decrire matiere, 775 diversite matiere, 776 classer materiaux, 768 grandes periodes histoire, 769 caracteristiques societe epoque, 791 besoin/objet technique
    })

# 938 - Decouvrir les bamboo pipe drums
set_activite(938,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants d" + chr(233) + "couvrent le D" + chr(224) + "n " + chr(272) + "inh P" + chr(225) + ", instrument traditionnel des hauts plateaux du Vietnam compos" + chr(233) + " de tubes de bambou frapp" + chr(233) + "s contre la paume. L\u2019activit" + chr(233) + " peut inclure la fabrication de tubes de longueurs diff" + chr(233) + "rentes, leur accord par ajustement, et l\u2019apprentissage de rythmes simples.",
    "D" + chr(233) + "couvrir un instrument de musique traditionnel d\u2019Asie du Sud-Est et explorer la relation entre la longueur d\u2019un tube de bambou et la hauteur du son produit.",
    "petit groupe", 60, tous,
    [120, 128, 60],   # Musique du monde, Traditions, Tige creuse
    [15, 4],           # Creer avec la nature, Connaitre nature
    {
        "Cycle 2": [622, 623, 624, 625, 650],
        # 622 experimenter sons, 623 ecoute attentive, 624 imaginer organisations sonores, 625 sensibilite, 650 fonctionnement objets
        "Cycle 3": [725, 726, 727, 728, 791, 797]
        # 725 techniques vocales/expressives, 726 caracteristiques musicales, 727 explorer sons nature, 728 sensibilite diversite, 791 besoin/objet technique, 797 demarche technologique
    })

# 939 - Depliant sur le cycle de vie
set_activite(939,
    "Int" + chr(233) + "rieur",
    "Les participants cr" + chr(233) + "ent un d" + chr(233) + "pliant accordéon en forme d\u2019animal : ferm" + chr(233) + ", il repr" + chr(233) + "sente l\u2019animal entier ; d" + chr(233) + "pli" + chr(233) + ", il r" + chr(233) + "v" + chr(232) + "le les diff" + chr(233) + "rentes " + chr(233) + "tapes de son cycle de vie (naissance, jeune, adulte). Chaque panneau de l\u2019accord" + chr(233) + "on est illustr" + chr(233) + " et l" + chr(233) + "gend" + chr(233) + ".",
    "Comprendre et repr" + chr(233) + "senter les " + chr(233) + "tapes du cycle de vie d\u2019un animal " + chr(224) + " travers une cr" + chr(233) + "ation visuelle interactive.",
    "individuel", 50, tous,
    [16, 14, 17],     # Developpement, Naissance, Reproduction
    [4, 15],           # Connaitre nature, Creer avec la nature
    {
        "Cycle 1": [564, 565, 523, 524, 556],
        # 564 etapes developpement vivant, 565 besoins animaux, 523 outils/mediums, 524 dessiner, 556 ordonner suite images
        "Cycle 2": [648, 617, 618, 655, 580],
        # 648 caracteristiques vivant, 617 productions plastiques, 618 reponses inventives, 655 se reperer temps, 580 representer relations alimentaires
        "Cycle 3": [784, 788, 758, 763, 785]
        # 784 richesse vivant, 788 cycle de vie plante/animal, 758 productions plastiques, 763 se reperer temps frise, 785 classer organismes
    })

# 940 - Deploiement des ailes de la coccinelle
set_activite(940,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants fabriquent une coccinelle en papier avec un m" + chr(233) + "canisme coulissant : en faisant glisser la coccinelle le long d\u2019un brin d\u2019herbe en papier, ses ailes rouges s\u2019ouvrent et r" + chr(233) + "v" + chr(232) + "lent une abeille cach" + chr(233) + "e en dessous.",
    "D" + chr(233) + "couvrir les insectes et leur biologie en cr" + chr(233) + "ant un m" + chr(233) + "canisme articulé en papier qui simule l\u2019ouverture des " + chr(233) + "lytres.",
    "individuel", 30, tous,
    [22, 37],     # Insectes, Ethologie
    [15, 5],       # Creer avec la nature, Decouvrir nature
    {
        "Cycle 1": [523, 524, 525, 564, 568],
        # 523 outils/mediums, 524 dessiner, 525 reproduire graphismes, 564 etapes developpement, 568 outils/materiaux
        "Cycle 2": [617, 618, 648, 650, 640],
        # 617 productions plastiques, 618 reponses inventives, 648 caracteristiques vivant, 650 fonctionnement objets, 640 regles vie collective
        "Cycle 3": [758, 784, 785, 791, 792]
        # 758 productions plastiques, 784 richesse vivant, 785 classer organismes, 791 besoin/objet technique, 792 distinguer objet technique/naturel
    })

db.commit()
db.close()
print("Lot 5 termine.")
