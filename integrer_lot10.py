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

# 581 - Photolangage feuille et fonctions
add(581, I,
    "Les participants s\u00e9lectionnent parmi 21 photographies de feuilles tr\u00e8s diverses (formes, tailles, couleurs, adaptations) celle qui les intrigue ou les surprend le plus. Les choix sont partag\u00e9s en groupe et ouvrent sur les fonctions des feuilles (photosynth\u00e8se, transpiration, protection).",
    "Explorer la diversit\u00e9 morphologique des feuilles et leurs fonctions, favoriser l\u2019expression orale et la curiosit\u00e9 botanique.",
    "grand groupe", 30, tous,
    [54,237,63],  # Anatomie vegetale, Photosynthese, Comportement vegetal
    [5,6],
    {"Cycle 1":[564,565,501,530,499],
     "Cycle 2":[648,604,607,639,573],
     "Cycle 3":[784,806,714,717,676]})

# 584 - Photolangage buissonnier en bois
add(584, I,
    "Les participants choisissent parmi 25 photographies de r\u00e9alisations en bois et en nature (abris, instruments, jouets, sculptures, cabanes, vannerie...) celle qui les inspire le plus ou qu\u2019ils aimeraient r\u00e9aliser. Les choix partagent en groupe stimulent l\u2019imagination et l\u2019envie de fabriquer.",
    "Stimuler l\u2019imagination cr\u00e9atrice et l\u2019envie de fabriquer, favoriser l\u2019expression orale en introduction d\u2019un atelier de fabrication nature.",
    "grand groupe", 25, tous,
    [121,122,128],  # Patrimoine, Representation de la nature, Traditions
    [17,15],
    {"Cycle 1":[501,530,531,568],
     "Cycle 2":[604,607,617,639],
     "Cycle 3":[714,717,758,728]})

# 201 - Poisson en feuille de chataignier
add(201, IE,
    "Les participants collectent une grande feuille de ch\u00e2taignier et y fixent des \u00e9l\u00e9ments naturels (p\u00e9tales, graines, mousses) pour cr\u00e9er un poisson d\u00e9coratif : la nervure centrale forme la ligne lat\u00e9rale, les autres nervures les ar\u00eates. L\u2019activit\u00e9 peut s\u2019accompagner d\u2019une d\u00e9couverte de l\u2019anatomie des poissons.",
    "D\u00e9velopper la cr\u00e9ativit\u00e9 et l\u2019observation des formes naturelles en cr\u00e9ant une \u0153uvre artistique \u00e9ph\u00e9m\u00e8re \u00e0 partir d\u2019une feuille de ch\u00e2taignier.",
    "individuel", 35, [9,10,11],  # automne
    [122,150,42],  # Representation de la nature, Anatomie animale, Regne vegetal
    [15,3],
    {"Cycle 1":[523,526,530,564],
     "Cycle 2":[617,618,620,648],
     "Cycle 3":[758,759,760,784]})

# 1250 - Porte plat savon en vannerie
add(1250, IE,
    "Les participants fabriquent un support circulaire en osier (porte-savon ou dessous-de-plat) selon la technique du fond catalan : formation d\u2019un cercle de base en osier, insertion de baguettes radiales et tressage de tiges de remplissage jusqu\u2019\u00e0 couvrir l\u2019int\u00e9rieur.",
    "Initier \u00e0 la vannerie en osier et fabriquer un objet utilitaire selon une technique ancestrale.",
    "individuel", 120, tous,
    [128,282],  # Traditions, Gestion durable ressources
    [15,18],
    {"Cycle 2":[617,619,650,648],
     "Cycle 3":[758,762,791,797,784]})

# 379 - Poterie primitive
add(379, IE,
    "Les participants apprennent \u00e0 modeler l\u2019argile selon des techniques ancestrales (colombin, pin\u00e7age) pour fabriquer un r\u00e9cipient. Les pi\u00e8ces sont d\u00e9cor\u00e9es avec des outils naturels (feuilles, brindilles, graines) laissant des empreintes, puis s\u00e9ch\u00e9es et \u00e9ventuellement cuites au feu de bois.",
    "D\u00e9couvrir les techniques de c\u00e9ramique primitive, comprendre la transformation de la mati\u00e8re par la chaleur et d\u00e9velopper la motricit\u00e9 fine.",
    "individuel", 90, tous,
    [75,128,121],  # Mineraux (argile), Traditions, Patrimoine
    [15,18],
    {"Cycle 1":[523,526,568,569,564],
     "Cycle 2":[617,619,646,650,648],
     "Cycle 3":[758,762,774,775,768]})
     # 768 grandes periodes histoire (Prehistoire)

db.commit()
db.close()
print("Lot 10 termine.")
