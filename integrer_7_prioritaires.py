import sqlite3

db_path = u'C:\\Users\\moina\\Dropbox\\Outils\\BDD activit\u00e9s\\_OUTIL\\activites.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Données à insérer
# format: (id, description, objectif_texte, format_groupe, duree_min, mois_list, thematique_ids, objectif_ids)
# météo : tout à 0 pour toutes

activites = [
    {
        'id': 226,
        'description': "Jeu d'expression orale où les enfants racontent tour à tour une courte anecdote vraie ou inventée. Le groupe vote pour décider si l'histoire est vraie ou fausse, puis le conteur révèle la réponse. Le conteur gagne s'il a réussi à tromper la majorité, sinon c'est le public qui gagne.",
        'objectif_texte': "S'exprimer en public et développer la cohésion de groupe à travers un jeu de devinette narrative.",
        'format_groupe': 'grand groupe',
        'duree_min': 40,
        'mois': list(range(1,13)),
        'thematique_ids': [126, 127],
        'objectif_ids': [17],
    },
    {
        'id': 293,
        'description': "Jeu coopératif où les enfants doivent, sans se parler ni se déplacer, faire en sorte qu'exactement X d'entre eux lèvent la main en 10 secondes. Les défis se complexifient progressivement (par genre, par zone, par caractéristique visible).",
        'objectif_texte': "Développer la coopération silencieuse, la stratégie collective et la gestion de la frustration.",
        'format_groupe': 'grand groupe',
        'duree_min': 30,
        'mois': list(range(1,13)),
        'thematique_ids': [125, 126],
        'objectif_ids': [16],
    },
    {
        'id': 486,
        'description': "L'animateur construit en direct une composition musicale par enregistrement en boucle (loopstation), à partir des sons produits par les enfants (voix, percussions, instruments). Une histoire est racontée et les enfants ajoutent des sons correspondant aux actions. Des jeux de danse et de statues s'intègrent à la séance.",
        'objectif_texte': "Créer collectivement une ambiance musicale et développer la créativité, l'écoute et l'expression corporelle.",
        'format_groupe': 'grand groupe',
        'duree_min': 45,
        'mois': list(range(1,13)),
        'thematique_ids': [],  # déjà en BDD : 120,126,249,240,246 - on ne modifie pas
        'objectif_ids': [15, 17],
    },
    {
        'id': 259,
        'description': "En extérieur, face à un arbre, un insecte et un animal, les enfants cherchent les points communs entre ces êtres vivants et eux-mêmes. Répartis en 5 groupes, ils miment chacun une des 5 caractéristiques du vivant (naître, grandir, se nourrir, se reproduire, mourir), puis les détaillent collectivement.",
        'objectif_texte': "Comprendre et mémoriser les 5 caractéristiques communes à tous les êtres vivants.",
        'format_groupe': 'petit groupe',
        'duree_min': 15,
        'mois': list(range(1,13)),
        'thematique_ids': [],  # déjà en BDD : 13 - on ajoute 14,15,17,16
        'thematique_ids_ajout': [14, 15, 16, 17],
        'objectif_ids': [4, 6],
    },
    {
        'id': 921,
        'description': "Les enfants partent seuls, l'un après l'autre, explorer un chemin en forêt jusqu'à un point de rendez-vous. L'animateur raconte ensuite l'histoire invisible de la forêt (animaux cachés, faune du sol) et propose des activités d'écoute collective. Une composition musicale est construite à la loopstation à partir des sons de la forêt et des enfants.",
        'objectif_texte': "Créer un lien sensoriel et émotionnel avec la forêt par l'exploration autonome et l'écoute musicale collective.",
        'format_groupe': 'grand groupe',
        'duree_min': 30,
        'mois': list(range(1,13)),
        'thematique_ids': [],  # déjà en BDD : 120,128,134,243 - on ne modifie pas
        'objectif_ids': [1, 2],
    },
    {
        'id': 1054,
        'description': "En forêt, les enfants observent les formes évocatrices de visages sur les troncs d'arbres, puis créent avec de l'argile et des éléments naturels le visage d'un arbre. Ils lui imaginent ensuite une histoire à raconter.",
        'objectif_texte': "Développer le lien affectif avec les arbres en combinant observation, création plastique et récit imaginaire.",
        'format_groupe': 'individuel',
        'duree_min': 90,
        'mois': [3,4,5,6,7,8,9,10,11],
        'thematique_ids': [122, 54],
        'objectif_ids': [15, 5],
    },
    {
        'id': 242,
        'description': "Les enfants récoltent des fleurs ou les observent en classe, les dessinent dans leur état entier puis décortiqué. Par groupes, ils comparent les différences entre fleurs mâles et femelles et se questionnent sur la reproduction des plantes. Des loupes permettent l'observation fine.",
        'objectif_texte': "Observer et comprendre les différences morphologiques entre fleurs et découvrir les mécanismes de reproduction végétale.",
        'format_groupe': 'petit groupe',
        'duree_min': 45,
        'mois': [4,5,6,7,8],
        'thematique_ids': [17, 54],
        'objectif_ids': [3, 6],
    },
]

# Colonnes mois
mois_cols = ['mois_janvier','mois_fevrier','mois_mars','mois_avril','mois_mai','mois_juin',
             'mois_juillet','mois_aout','mois_septembre','mois_octobre','mois_novembre','mois_decembre']

for a in activites:
    aid = a['id']
    print(f"\nTraitement ID {aid}...")

    # Mise à jour des champs de base
    mois_vals = {col: (1 if (i+1) in a['mois'] else 0) for i, col in enumerate(mois_cols)}
    
    cur.execute("""
        UPDATE activite SET
            description = ?,
            objectif_texte = ?,
            format_groupe = ?,
            duree_min = ?,
            mois_janvier=?, mois_fevrier=?, mois_mars=?, mois_avril=?, mois_mai=?, mois_juin=?,
            mois_juillet=?, mois_aout=?, mois_septembre=?, mois_octobre=?, mois_novembre=?, mois_decembre=?
        WHERE id = ?
    """, (
        a['description'], a['objectif_texte'], a['format_groupe'], a['duree_min'],
        *[mois_vals[c] for c in mois_cols],
        aid
    ))
    print(f"  -> champs de base mis à jour")

    # Thématiques : insertion (sauf si déjà existantes)
    thematiques_a_ajouter = a.get('thematique_ids', []) + a.get('thematique_ids_ajout', [])
    for tid in thematiques_a_ajouter:
        cur.execute("SELECT 1 FROM activite_thematique WHERE activite_id=? AND thematique_id=?", (aid, tid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_thematique (activite_id, thematique_id) VALUES (?,?)", (aid, tid))
            print(f"  -> thématique {tid} ajoutée")
        else:
            print(f"  -> thématique {tid} déjà présente")

    # Objectifs : insertion (sauf si déjà existants)
    for oid in a.get('objectif_ids', []):
        cur.execute("SELECT 1 FROM activite_objectif WHERE activite_id=? AND objectif_id=?", (aid, oid))
        if not cur.fetchone():
            cur.execute("INSERT INTO activite_objectif (activite_id, objectif_id) VALUES (?,?)", (aid, oid))
            print(f"  -> objectif {oid} ajouté")
        else:
            print(f"  -> objectif {oid} déjà présent")

conn.commit()
conn.close()
print("\nDone.")
