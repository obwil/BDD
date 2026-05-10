import sys, sqlite3
sys.stdout.reconfigure(encoding="utf-8")
db = sqlite3.connect(r"C:\Users\moina\Dropbox\Outils\BDD activit" + chr(233) + r"s\_OUTIL\activites.db")
cur = db.cursor()

# Recuperer les cycle_ids
cur.execute("SELECT id, nom FROM cycle")
cycles = {r[1]: r[0] for r in cur.fetchall()}
print("Cycles:", cycles)

def set_activite(aid, lieu, desc, obj_txt, fmt, duree, mois, themes, objectifs, cycles_attendus):
    # Champs de base
    mois_vals = [1 if (i+1) in mois else 0 for i in range(12)]
    cur.execute("""UPDATE activite SET lieu=?,description=?,objectif_texte=?,format_groupe=?,duree_min=?,
        mois_jan=?,mois_fev=?,mois_mar=?,mois_avr=?,mois_mai=?,mois_jun=?,
        mois_jul=?,mois_aou=?,mois_sep=?,mois_oct=?,mois_nov=?,mois_dec=?
        WHERE id=?""",
        (lieu, desc, obj_txt, fmt, duree, *mois_vals, aid))
    print(f"ID {aid}: champs base OK")

    # Thematiques
    for tid in themes:
        cur.execute("SELECT 1 FROM activite_thematique WHERE activite_id=? AND thematique_id=?", (aid, tid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_thematique(activite_id,thematique_id) VALUES(?,?)", (aid, tid))
            print(f"  thematique {tid} ajoutee")

    # Objectifs
    for oid in objectifs:
        cur.execute("SELECT 1 FROM activite_objectif WHERE activite_id=? AND objectif_id=?", (aid, oid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_objectif(activite_id,objectif_id) VALUES(?,?)", (aid, oid))
            print(f"  objectif {oid} ajoute")

    # Cycles + attendus
    for cycle_nom, attendu_ids in cycles_attendus.items():
        cid = cycles[cycle_nom]
        # Cycle
        cur.execute("SELECT 1 FROM activite_cycle WHERE activite_id=? AND cycle_id=?", (aid, cid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_cycle(activite_id,cycle_id) VALUES(?,?)", (aid, cid))
            print(f"  cycle {cycle_nom} ajoute")
        # Statut ok dans activite_cycle_analysee
        cur.execute("SELECT 1 FROM activite_cycle_analysee WHERE activite_id=? AND cycle_id=?", (aid, cid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_cycle_analysee(activite_id,cycle_id,statut) VALUES(?,?,'ok')", (aid, cid))
        else:
            cur.execute("UPDATE activite_cycle_analysee SET statut='ok' WHERE activite_id=? AND cycle_id=?", (aid, cid))
        # Attendus
        for att_id in attendu_ids:
            cur.execute("SELECT 1 FROM activite_attendu WHERE activite_id=? AND attendu_id=?", (aid, att_id))
            if not cur.fetchone():
                cur.execute("INSERT INTO activite_attendu(activite_id,attendu_id) VALUES(?,?)", (aid, att_id))
                print(f"  attendu {att_id} ajoute (cycle {cycle_nom})")

tous = list(range(1,13))

# 1425 - Chaine alimentaire
set_activite(1425,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Activit" + chr(233) + " de construction de cha" + chr(238) + "nes alimentaires " + chr(224) + " l\u2019aide de supports vari" + chr(233) + "s : anneaux, gobelets, " + chr(233) + "lastiques, cartes ou accord" + chr(233) + "on. Les enfants relient les organismes entre eux pour visualiser les relations de pr" + chr(233) + "dation.",
    "Comprendre le fonctionnement d\u2019une cha" + chr(238) + "ne alimentaire et les relations entre producteurs, consommateurs et d" + chr(233) + "composeurs.",
    "petit groupe", 30, tous, [190, 176], [6],
    {"Cycle 2": [580, 648, 581], "Cycle 3": [806, 807, 674]})

# 918 - Affiche nocturne
set_activite(918,
    "Int" + chr(233) + "rieur",
    "Les enfants fabriquent une affiche interactive simulant une sc" + chr(232) + "ne nocturne : ils dessinent au feutre ind" + chr(233) + "l" + chr(233) + "bile sur une pochette plastique transparente pos" + chr(233) + "e sur fond noir, puis cr" + chr(233) + "ent une \u00ab\u00a0lampe torche\u00a0\u00bb en papier qu\u2019ils glissent dans la pochette pour r" + chr(233) + "v" + chr(233) + "ler progressivement les animaux nocturnes cach" + chr(233) + "s.",
    "D" + chr(233) + "velopper l\u2019observation et la curiosit" + chr(233) + " sur les animaux nocturnes " + chr(224) + " travers une activit" + chr(233) + " de cr" + chr(233) + "ation manuelle.",
    "individuel", 45, tous, [37, 122], [5, 15],
    {"Cycle 1": [523, 524], "Cycle 2": [617, 648]})

# 919 - Ananas en feuilles
set_activite(919,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "Les enfants r" + chr(233) + "coltent des feuilles longues et souples, puis les tressent selon une technique traditionnelle pour cr" + chr(233) + "er un petit ananas d" + chr(233) + "coratif. L\u2019activit" + chr(233) + " mobilise la dext" + chr(233) + "rit" + chr(233) + " fine et valorise les mat" + chr(233) + "riaux naturels glan" + chr(233) + "s.",
    "D" + chr(233) + "velopper la dext" + chr(233) + "rit" + chr(233) + " manuelle et d" + chr(233) + "couvrir une technique de tressage v" + chr(233) + "g" + chr(233) + "tal traditionnelle.",
    "individuel", 60, tous, [128], [15],
    {"Cycle 1": [523, 526], "Cycle 2": [617, 619]})

# 5 - Anim oiseaux migration LPO
set_activite(5,
    "Int" + chr(233) + "rieur/Ext" + chr(233) + "rieur",
    "S" + chr(233) + "quence d\u2019animations sur la migration des oiseaux combinant apports en salle (mythes, d" + chr(233) + "finitions, jeu de passeports), jeux ext" + chr(233) + "rieurs (" + chr(233) + "pervier " + chr(233) + "cologique, \u00ab\u00a0migrer pour les bonnes raisons\u00a0\u00bb) et contes. Les enfants d" + chr(233) + "couvrent pourquoi et comment les oiseaux migrent, leurs dangers, et s\u2019exercent " + chr(224) + " l\u2019empathie et " + chr(224) + " la coop" + chr(233) + "ration.",
    "Comprendre le ph" + chr(233) + "nom" + chr(232) + "ne migratoire chez les oiseaux (causes, m" + chr(233) + "canismes, dangers) et d" + chr(233) + "velopper l\u2019empathie envers le vivant.",
    "grand groupe", 120, [3,4,8,9,10], [37, 20], [4, 6],
    {"Cycle 2": [648, 574, 638], "Cycle 3": [784, 673]})

# 236 - Automates
set_activite(236,
    "Int" + chr(233) + "rieur",
    "Les participants fabriquent des automates inspir" + chr(233) + "s de la nature \u2014 petits m" + chr(233) + "canismes en carton reproduisant le mouvement d\u2019un animal (oiseau, insecte, dinosaure). Ils choisissent un patron, d" + chr(233) + "coupent, colorient et assemblent un m" + chr(233) + "canisme simple (pince " + chr(224) + " linge, levier, attache parisienne) cr" + chr(233) + "ant l\u2019illusion du mouvement, puis pr" + chr(233) + "sentent leur automate au groupe.",
    "Explorer le lien entre m" + chr(233) + "canique et biologie en reproduisant le mouvement animal par la fabrication d\u2019un automate.",
    "individuel", 75, tous, [37, 297], [15, 6],
    {"Cycle 2": [650, 617], "Cycle 3": [791, 792, 796]})

db.commit()
db.close()
print("Termine.")
