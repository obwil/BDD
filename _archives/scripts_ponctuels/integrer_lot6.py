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

# 1227 - Jeu de plateau de poursuite
set_activite(1227,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Jeu de plateau strat" + chr(233) + "gique " + chr(224) + " deux joueurs sur un r" + chr(233) + "seau de points reli" + chr(233) + "s par des chemins. L\u2019un joue le poursuivant, l\u2019autre le poursuivi ; chacun avance d\u2019un point par tour. Le poursuivant gagne en atteignant le point du poursuivi. Le plateau peut " + chr(233) + "galement " + chr(234) + "tre jou" + chr(233) + " en grandeur nature dans la nature.",
    "D" + chr(233) + "velopper la strat" + chr(233) + "gie, l\u2019anticipation et la logique spatiale.",
    "binome", 20, tous,
    [125, 161],   # Jeux cooperatifs, Ecologie (thematique relation proie-predateur)
    [16, 12],      # Jouer dans nature, Se reperer
    {
        "Cycle 1": [558, 559, 560, 522, 535],
        # 558 situer objets, 559 se situer, 560 realiser trajet, 522 cooperer roles, 535 utiliser nombre position
        "Cycle 2": [634, 636, 637, 668, 643],
        # 634 affrontement regles, 636 connaitre but jeu, 637 reconnaitre partenaires/adversaires, 668 se situer espace, 643 participer groupe
        "Cycle 3": [744, 745, 746, 747, 748]
        # 744 s organiser tactiquement, 745 maintenir engagement, 746 respecter partenaires, 747 roles sociaux, 748 accepter resultat
    })

# 1228 - Jeu de pog a l ancienne avec des cartes
set_activite(1228,
    "Ext" + chr(233) + "rieur",
    "Les participants fabriquent des \u00ab\u00a0plioirs\u00a0\u00bb en pliant des cartes " + chr(224) + " jouer recycl" + chr(233) + "es en plusieurs " + chr(233) + "paisseurs, puis s\u2019affrontent en lan" + chr(231) + "ant leurs plioirs pour retourner ceux des adversaires. Le joueur qui collecte le plus de plioirs retourne gagne.",
    "D" + chr(233) + "velopper l\u2019adresse et la coordination tout en jouant avec du mat" + chr(233) + "riel recycl" + chr(233) + ".",
    "grand groupe", 35, tous,
    [125, 117],   # Jeux cooperatifs, Cultures
    [16],          # Jouer dans nature
    {
        "Cycle 1": [517, 518, 519, 522, 568],
        # 517 courir/sauter/lancer, 518 ajuster actions, 519 se deplacer securite, 522 cooperer, 568 outils/materiaux
        "Cycle 2": [626, 628, 629, 634, 636],
        # 626 courir/sauter/lancer, 628 viser performance, 629 roles specifiques, 634 affrontement regles, 636 connaitre but jeu
        "Cycle 3": [734, 744, 746, 747, 748]
        # 734 realiser efforts, 744 s organiser, 746 respecter, 747 roles sociaux, 748 accepter resultat
    })

# 258 - Jeu des animaux camoufl" + chr(233) + "s dans une image
set_activite(258,
    "Int" + chr(233) + "rieur",
    "Les participants observent des photographies de milieux naturels dans lesquelles des animaux sont camoufl" + chr(233) + "s. Le d" + chr(233) + "fi consiste " + chr(224) + " rep" + chr(233) + "rer tous les animaux cach" + chr(233) + "s. L\u2019activit" + chr(233) + " est enrichie par une discussion sur les strat" + chr(233) + "gies de camouflage (mim" + chr(233) + "tisme chromatique, de forme, comportement immobile).",
    "Comprendre les m" + chr(233) + "canismes du camouflage animal, d" + chr(233) + "velopper l\u2019observation fine et d" + chr(233) + "couvrir la biodiversit" + chr(233) + " cach" + chr(233) + "e dans les milieux naturels.",
    "individuel", 30, tous,
    [37, 158, 20],   # Ethologie, Adaptation, Groupes animaux
    [3, 4],           # Observer nature, Connaitre nature
    {
        "Cycle 1": [564, 565, 570, 499, 500],
        # 564 etapes developpement, 565 besoins animaux, 570 objets numeriques, 499 reformuler propos, 500 reformuler propos autrui
        "Cycle 2": [648, 574, 601, 604, 607],
        # 648 caracteristiques vivant, 574 interactions humain/vivant, 601 demarche investigation numerique, 604 ecoute, 607 participer echange
        "Cycle 3": [784, 785, 806, 714, 717]
        # 784 richesse vivant, 785 classer organismes, 806 decrire ecosysteme, 714 ecouter recit, 717 echanges constructifs
    })

# 611 - Jeu sur les animaux de la foret
set_activite(611,
    "Int" + chr(233) + "rieur",
    "Les enfants re" + chr(231) + "oivent des images d\u2019animaux et doivent les associer au type de for" + chr(234) + "t qui leur correspond ainsi qu\u2019" + chr(224) + " la bonne taille de for" + chr(234) + "t. L\u2019activit" + chr(233) + " permet de comprendre les besoins sp" + chr(233) + "cifiques de chaque esp" + chr(232) + "ce et ce qu\u2019on peut trouver dans les for" + chr(234) + "ts de proximit" + chr(233) + ".",
    "Comprendre les besoins des animaux forestiers et les relations entre les esp" + chr(232) + "ces et leur habitat.",
    "petit groupe", 25, tous,
    [37, 20, 167],   # Ethologie, Groupes animaux, Ecologie du paysage
    [4, 6],           # Connaitre nature, Comprendre nature
    {
        "Cycle 1": [564, 565, 558, 563, 500],
        # 564 etapes developpement, 565 besoins animaux/vegetaux, 558 situer objets, 563 marqueurs spatiaux, 500 reformuler autrui
        "Cycle 2": [648, 658, 574, 653, 607],
        # 648 caracteristiques vivant, 658 interactions mode de vie/environnement, 574 interactions humain/vivant, 653 se reperer espace, 607 participer echange
        "Cycle 3": [784, 806, 808, 785, 672]
        # 784 richesse vivant, 806 decrire ecosysteme, 808 consequences action humaine, 785 classer organismes, 672 enjeux preservation biodiversite
    })

# 469 - Kamishibai - l eau a travers le temps
set_activite(469,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "L\u2019animateur raconte l\u2019histoire de l\u2019eau " + chr(224) + " travers les " + chr(226) + "ges " + chr(224) + " l\u2019aide d\u2019un kamishibai (th" + chr(233) + " + chr(226) + "tre d\u2019images japonnais). Le r" + chr(233) + "cit retrace les diff" + chr(233) + "rentes formes et usages de l\u2019eau depuis les origines, invitant les enfants " + chr(224) + " r" + chr(233) + "fl" + chr(233) + "chir sur l\u2019importance de cette ressource.",
    "D" + chr(233) + "couvrir l\u2019histoire et les usages de l\u2019eau " + chr(224) + " travers les civilisations, et sensibiliser " + chr(224) + " sa valeur comme bien commun.",
    "grand groupe", 30, tous,
    [221, 163, 686],  # L eau, Cycle eau, Usages eau (sous-domaine EDD)
    [6, 1],            # Comprendre nature, Connexion nature
    {
        "Cycle 1": [482, 483, 484, 501, 555],
        # 482 presence eau environnement, 483 usages eau, 484 interrogations usages eau, 501 usages langue orale, 555 situer evenements temps
        "Cycle 2": [586, 587, 588, 589, 604, 656],
        # 586 reservoirs eau, 587 usages eau bien commun, 588 incidences comportement eau, 589 solutions gaspillage, 604 ecoute, 656 situer evenements temps long
        "Cycle 3": [684, 686, 687, 691, 692, 714]
        # 684 cycle eau, 686 relier cycle/usages, 687 ecarts disponibilite/usages, 691 eau bien commun, 692 valeurs gestion eau, 714 ecouter recit
    })

db.commit()
db.close()
print("Lot 6 termine.")
