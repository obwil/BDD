import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
db = sqlite3.connect(r"C:\Users\moina\Dropbox\Outils\BDD activit" + chr(233) + r"s\_OUTIL\activites.db")
cur = db.cursor()
cur.execute("SELECT id, nom FROM cycle")
cycles = {r[1]: r[0] for r in cur.fetchall()}

def set_activite(aid, lieu, desc, obj_txt, fmt, duree, mois, themes, objectifs, cycles_attendus):
    mois_vals = [1 if (i+1) in mois else 0 for i in range(12)]
    cur.execute("""UPDATE activite SET lieu=?,description=?,objectif_texte=?,format_groupe=?,duree_min=?,
        mois_jan=?,mois_fev=?,mois_mar=?,mois_avr=?,mois_mai=?,mois_jun=?,
        mois_jul=?,mois_aou=?,mois_sep=?,mois_oct=?,mois_nov=?,mois_dec=?
        WHERE id=?""", (lieu,desc,obj_txt,fmt,duree,*mois_vals,aid))
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

# 923 - Claves naturelles
set_activite(923,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les participants s" + chr(233) + "lectionnent des branches ou tiges de bois sec de diff" + chr(233) + "rentes essences, testent leurs sonorit" + chr(233) + "s en les percutant, puis taillent leurs claves " + chr(224) + " la bonne longueur. Ils apprennent ensuite des rythmes de base (clave 3-2 et 2-3 du son cubain) et explorent les diff" + chr(233) + "rences de timbre selon le bois.",
    "Explorer les propri" + chr(233) + "t" + chr(233) + "s sonores du bois et d" + chr(233) + "couvrir un instrument de percussion fondamental de la musique latine.",
    "petit groupe", 45, tous,
    [120, 128, 134],  # Musique du monde, Traditions, Audition
    [15, 5],  # Creer avec la nature, Decouvrir la nature
    {
        "Cycle 2": [622, 623, 624, 617, 648],
        # 622 experimenter voix/sons, 623 ecoute attentive, 624 imaginer organisations sonores, 617 productions plastiques, 648 caracteristiques vivant
        "Cycle 3": [725, 727, 728, 758, 784]
        # 725 techniques vocales/corporelles, 727 explorer sons nature, 728 sensibilite diversite, 758 productions plastiques 3D, 784 richesse vivant
    })

# 924 - Cliquet en bambou
set_activite(924,
    "Ext" + chr(233) + "rieur",
    "Fabrication artisanale d\u2019un cliquet (carracla) en bambou : s" + chr(233) + "lection et d" + chr(233) + "coupe d\u2019une section de bambou, r" + chr(233) + "alisation de rainures longitudinales, fabrication d\u2019un pignon en bois et assemblage sur axe m" + chr(233) + "tallique. L\u2019instrument produit un son caract" + chr(233) + "ristique lorsqu\u2019on le fait tourner.",
    "D" + chr(233) + "couvrir les techniques de travail du bambou et cr" + chr(233) + "er un instrument de percussion traditionnel fonctionnel.",
    "individuel", 90, tous,
    [120, 128],  # Musique du monde, Traditions
    [15, 18],   # Creer avec la nature, Construire dans la nature
    {
        "Cycle 2": [617, 619, 622, 623, 650],
        # 617 productions plastiques, 619 cooperer projet artistique, 622 experimenter sons, 623 ecoute, 650 fonctionnement objets fabriques
        "Cycle 3": [758, 762, 725, 727, 791, 797]
        # 758 productions plastiques, 762 projet artistique, 725 techniques expressives, 727 explorer sons, 791 besoin/objet technique, 797 demarche technologique
    })

# 926 - Construire et utiliser des des forestiers (Puluque)
set_activite(926,
    "Ext" + chr(233) + "rieur",
    "Les participants fabriquent leurs propres d" + chr(233) + "s en bois (bouts de bois taill" + chr(233) + "s avec face plate et face arrondie) et jouent au Puluque, jeu de soci" + chr(233) + "t" + chr(233) + " traditionnel guatemalt" + chr(232) + "que : sur un plateau de brindilles, ils d" + chr(233) + "placent des feuilles-pions et cherchent " + chr(224) + " capturer celles de l\u2019adversaire.",
    "D" + chr(233) + "couvrir un jeu traditionnel d\u2019une autre culture et d" + chr(233) + "velopper strat" + chr(233) + "gie, coop" + chr(233) + "ration et connaissance des v" + chr(233) + "g" + chr(233) + "taux locaux.",
    "binome", 45, tous,
    [128, 117, 125],  # Traditions, Cultures, Jeux cooperatifs
    [16, 5],          # Jouer dans la nature, Decouvrir la nature
    {
        "Cycle 1": [568, 560, 522, 564, 501],
        # 568 outils/materiaux, 560 se situer espace, 522 cooperer roles complementaires, 564 etapes developpement vivant, 501 divers usages langue orale
        "Cycle 2": [638, 643, 645, 648, 658],
        # 638 respecter autrui, 643 participer groupe, 645 ecouter/argumenter, 648 caracteristiques vivant, 658 interactions mode de vie/environnement
        "Cycle 3": [749, 754, 757, 784, 674]
        # 749 respecter autrui, 754 membre collectivite, 757 ecouter/justifier, 784 richesse vivant, 674 biodiversite bien commun
    })

# 423 - Conte - l arbre triste
set_activite(423,
    "Ext" + chr(233) + "rieur",
    "L\u2019animateur raconte l\u2019histoire d\u2019un arbre qui pleure parce qu\u2019il se sent oubli" + chr(233) + " des hommes. L\u2019arbre " + chr(233) + "voque la culture celte, le respect des arbres et de la for" + chr(234) + "t, et demande aux enfants de l\u2019aider " + chr(224) + " retrouver sa place dans la m" + chr(233) + "moire humaine.",
    "D" + chr(233) + "velopper le lien affectif avec les arbres et la for" + chr(234) + "t en mobilisant l\u2019imaginaire et la symbolique culturelle celte.",
    "grand groupe", 30, tous,
    [123, 128, 122],  # Celtes, Traditions, Representation de la nature
    [1, 2, 17],       # Connexion nature, Ressentir nature, Imaginer
    {
        "Cycle 1": [501, 502, 530, 564, 572],
        # 501 usages langue orale, 502 comptines/poesies, 530 decrire image/musique/ressenti, 564 etapes developpement vivant, 572 attitude responsable protection vivant
        "Cycle 2": [604, 606, 607, 639, 573, 575],
        # 604 ecoute situations echanges, 606 raconter/decrire, 607 participer echange, 639 partager emotions, 573 sensible incidences comportement biodiversite, 575 biodiversite bien commun
        "Cycle 3": [714, 717, 750, 755, 674, 676]
        # 714 ecouter recit/comprendre, 717 participer echanges constructifs, 750 partager emotions vocabulaire adapte, 755 conscience civique ecologique, 674 biodiversite bien commun, 676 valeurs attribuees nature
    })

# 669 - Conte philosophique sur l oeuf
set_activite(669,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Lecture ou narration du conte philosophique \u00ab\u00a0L\u2019\u0152uf\u00a0\u00bb (Andy Weir) : un homme mort rencontre Dieu qui lui r" + chr(233) + "v" + chr(232) + "le qu\u2019il est la r" + chr(233) + "incarnation de tous les " + chr(234) + "tres vivants ayant jamais exist" + chr(233) + ". Le conte ouvre sur des questions d\u2019empathie universelle et de lien entre tous les vivants.",
    "Provoquer une r" + chr(233) + "flexion philosophique sur le lien entre tous les " + chr(234) + "tres vivants et d" + chr(233) + "velopper l\u2019empathie envers le vivant.",
    "grand groupe", 30, tous,
    [126, 122, 161],  # Vivre ensemble, Representation de la nature, Ecologie
    [1, 6, 17],       # Connexion nature, Comprendre nature, Imaginer
    {
        "Cycle 2": [604, 606, 639, 644, 645, 573],
        # 604 ecoute, 606 raconter/decrire, 639 partager emotions, 644 interet personnel vs general, 645 ecouter/argumenter, 573 sensible biodiversite
        "Cycle 3": [714, 717, 750, 756, 757, 676, 674]
        # 714 ecouter recit, 717 echanges constructifs, 750 partager emotions, 756 reflexion critique, 757 justifier point de vue, 676 valeurs nature, 674 biodiversite bien commun
    })

db.commit()
db.close()
print("Lot 2 termine.")
