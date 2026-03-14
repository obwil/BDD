# =============================================================================
# import_pedagogies.py
# =============================================================================
# Peuple les tables pedagogie et theorie_apprentissage dans SQLite.
# Les résumés sont issus des pages Notion correspondantes.
# Idempotent : utilise INSERT OR IGNORE.
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

# =============================================================================
# DONNÉES : PÉDAGOGIES
# Résumés synthétisés depuis les pages Notion
# =============================================================================

PEDAGOGIES = [
    {
        "nom": "Apprentissage par problèmes",
        "resume": (
            "L'apprenant est confronté à un problème authentique et mal structuré qu'il doit "
            "résoudre de façon collaborative sans formation préalable spécifique. L'enseignant "
            "joue un rôle de facilitateur. Favorise l'autonomie, la pensée critique et le "
            "transfert des connaissances dans des contextes réels."
        ),
        "notion_url": "https://www.notion.so/22d57d3941e880bab6efd12fd72df247"
    },
    {
        "nom": "Apprentissage coopératif, collaboratif et pluriel",
        "resume": (
            "Les apprenants travaillent ensemble vers un objectif commun en s'appuyant sur "
            "l'interdépendance positive, la responsabilité individuelle et les interactions "
            "constructives. Développe les compétences sociales, la communication et "
            "l'intelligence collective."
        ),
        "notion_url": "https://www.notion.so/22d57d3941e880c48171e26308c074bf"
    },
    {
        "nom": "Apprentissage expérientiel",
        "resume": (
            "L'apprentissage se construit par l'expérience directe suivie d'une réflexion "
            "structurée (cycle de Kolb : expérience -> observation -> conceptualisation -> "
            "expérimentation). Le vécu corporel et sensoriel est central. Particulièrement "
            "adapté aux activités en plein air et à l'éducation à la nature."
        ),
        "notion_url": "https://www.notion.so/22d57d3941e88067b63bd361b60340a7"
    },
    {
        "nom": "Apprentissage par l'enquête",
        "resume": (
            "L'apprenant formule des questions, émet des hypothèses et mène une investigation "
            "pour y répondre, en adoptant une démarche scientifique. L'enseignant guide sans "
            "donner les réponses. Développe la curiosité, la rigueur méthodologique et "
            "l'autonomie intellectuelle."
        ),
        "notion_url": "https://www.notion.so/22d57d3941e880638282c06bdf859efa"
    },
    {
        "nom": "Apprentissage par projets",
        "resume": (
            "Les apprenants réalisent un projet concret et signifiant sur une période étendue, "
            "mobilisant des connaissances pluridisciplinaires. Le produit final est réel et "
            "destiné à un public. Développe la planification, la persévérance et le sens "
            "des responsabilités."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e880738557f8c40215d864"
    },
    {
        "nom": "Pédagogie de l'Imprévu",
        "resume": (
            "S'appuie sur les événements spontanés et les opportunités imprévues de "
            "l'environnement immédiat pour générer des apprentissages. L'animateur saisit "
            "les moments de curiosité naturelle des enfants. Particulièrement adaptée à "
            "l'éducation en pleine nature où l'imprévu est constant."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e880609c8fdb55f2935c90"
    },
    {
        "nom": "Pédagogie par alternance",
        "resume": (
            "Alterne les temps en milieu naturel/terrain et les temps d'analyse et de "
            "conceptualisation en intérieur. L'expérience de terrain nourrit la réflexion "
            "théorique et vice versa. Crée des allers-retours entre le concret et l'abstrait."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e8808fab02d9977e827898"
    },
    {
        "nom": "Pédagogie différenciée",
        "resume": (
            "Adapte les contenus, processus et productions aux besoins, rythmes et styles "
            "d'apprentissage de chaque apprenant. Propose des entrées multiples pour un même "
            "objectif. Particulièrement utile dans des groupes hétérogènes en âge ou en "
            "niveau."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e88018b021e1e6ca5919a7"
    },
    {
        "nom": "Pédagogie explicite",
        "resume": (
            "L'enseignant modélise explicitement les stratégies et savoirs visés avant de "
            "laisser l'apprenant pratiquer progressivement de façon guidée puis autonome "
            "(je fais -> nous faisons -> vous faites). Efficace pour l'acquisition de "
            "compétences techniques précises."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e880b1b7f1f8871f1e1dbc"
    },
    {
        "nom": "Classe inversée",
        "resume": (
            "La transmission d'information se fait en dehors de la séance (lecture, vidéo) "
            "et le temps en groupe est consacré à la pratique, aux échanges et à "
            "l'approfondissement. Libère le temps collectif pour les activités à haute "
            "valeur ajoutée."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e8806b8c8ae1ba22c1888c"
    },
    {
        "nom": "Le jeu et la gamification",
        "resume": (
            "Utilise les mécaniques du jeu (règles, défi, récompense, progression, plaisir) "
            "au service des apprentissages. Le jeu est un vecteur naturel d'engagement, "
            "d'exploration et de prise de risque sans enjeu réel. Particulièrement puissant "
            "avec les jeunes enfants."
        ),
        "notion_url": "https://www.notion.so/22a57d3941e880cba4b4ee0a82a47988"
    },
    {
        "nom": "Enseignement réciproque",
        "resume": (
            "Les apprenants s'enseignent mutuellement : expliquer aux autres consolide et "
            "révèle les lacunes. Alterne les rôles de tuteur et d'apprenant. Développe "
            "la métacognition, la communication et la solidarité dans le groupe."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e8807087b0d4e47f9f2403"
    },
    {
        "nom": "Théorie de l'apprentissage transformatif",
        "resume": (
            "L'apprentissage profond implique une transformation des cadres de référence "
            "et des représentations du monde (Mezirow). Une expérience déstabilisante "
            "déclenche une réflexion critique qui aboutit à un changement de perspective "
            "durable."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e880ee9868ff60a7e5e176"
    },
    {
        "nom": "Spécificités Freinet, Montessori, Steiner",
        "resume": (
            "Trois pédagogies alternatives partageant le respect du rythme de l'enfant et "
            "l'importance de l'environnement préparé. Freinet : tâtonnement expérimental et "
            "production réelle. Montessori : matériel sensoriel et autonomie. Steiner : "
            "développement artistique et cycles de l'enfance."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e8803492dee7375f05ed2e"
    },
    {
        "nom": "Théorie instructionnelle de Gagné",
        "resume": (
            "Identifie neuf événements d'instruction (attirer l'attention, énoncer l'objectif, "
            "rappeler les prérequis, présenter le contenu, guider l'apprentissage, provoquer "
            "la performance, donner un feedback, évaluer, favoriser la rétention et le "
            "transfert). Fournit un cadre structuré pour la conception pédagogique."
        ),
        "notion_url": "https://www.notion.so/24b57d3941e8814e873af9b79f88b51f"
    },
    {
        "nom": "Pédagogie de l'Imaginaire",
        "resume": (
            "Mobilise l'imagination, le conte, la métaphore et le symbolique comme vecteurs "
            "d'apprentissage et de connexion au vivant. L'histoire crée un espace intérieur "
            "qui facilite l'identification et l'émotion, ouvrant à des apprentissages "
            "profonds et durables."
        ),
        "notion_url": "https://www.notion.so/22957d3941e880deb127efb1bbd13397"
    },
    {
        "nom": "Pédagogie du lieu",
        "resume": (
            "Le lieu lui-même (forêt, mare, quartier, paysage) est le principal vecteur "
            "pédagogique. L'apprenant développe un lien intime avec un espace particulier "
            "qui devient support d'apprentissages écologiques, sensoriels et identitaires. "
            "Le 'sit spot' en est une application emblématique."
        ),
        "notion_url": "https://www.notion.so/22957d3941e8807b8f0fd296e502af87"
    },
    {
        "nom": "L'approche Tête-Cœur-Mains",
        "resume": (
            "Équilibre trois dimensions : cognitive (Tête : comprendre, analyser), affective "
            "(Cœur : ressentir, s'engager) et pratique (Mains : faire, créer). Inspirée de "
            "Pestalozzi et Steiner. Particulièrement adaptée à l'éducation à l'environnement "
            "qui cherche à toucher l'être dans sa globalité."
        ),
        "notion_url": "https://www.notion.so/22857d3941e880f491e3db13d0d6a720"
    },
    {
        "nom": "Cognitivisme pédagogique",
        "resume": (
            "S'intéresse aux processus mentaux internes : attention, mémoire, représentations, "
            "schémas cognitifs. L'apprentissage est une restructuration des connaissances "
            "existantes. Implique de tenir compte de la charge cognitive et d'organiser "
            "l'information pour faciliter son encodage et sa rétention."
        ),
        "notion_url": "https://www.notion.so/22d57d3941e880708aeeea4a8c8d95c6"
    },
]

# =============================================================================
# DONNÉES : THÉORIES D'APPRENTISSAGE
# =============================================================================

THEORIES = [
    {
        "nom": "Behaviorisme",
        "resume": (
            "L'apprentissage est un changement de comportement observable produit par des "
            "stimuli et des renforcements (Pavlov, Skinner). L'environnement conditionne les "
            "réponses de l'apprenant. Utile pour l'acquisition d'automatismes et de réflexes "
            "de sécurité en nature."
        ),
        "notion_url": "https://www.notion.so/22c57d3941e880ad9d8af38d9bbe6352"
    },
    {
        "nom": "Constructivisme piagetien",
        "resume": (
            "L'apprenant construit activement ses connaissances par interaction avec "
            "l'environnement, à travers l'assimilation et l'accommodation (Piaget). "
            "Le développement cognitif suit des stades universels. L'action physique sur "
            "le réel est fondamentale pour les jeunes enfants."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e880a6a881d94bc311fea0"
    },
    {
        "nom": "Constructivisme humaniste",
        "resume": (
            "Intègre la dimension affective et motivationnelle dans l'apprentissage (Rogers, "
            "Maslow). L'apprenant apprend mieux dans un climat de confiance, de respect et "
            "d'authenticité. La relation éducative et le sentiment de sécurité sont des "
            "conditions préalables."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e880bb87c2ff90ce0c0216"
    },
    {
        "nom": "Constructivisme social de Bruner",
        "resume": (
            "La culture et le langage sont des outils de pensée (Bruner). L'apprentissage "
            "est facilité par la narration, l'échafaudage (scaffolding) et la mise en récit. "
            "Le curriculum en spirale revisité progressivement permet une compréhension de "
            "plus en plus profonde."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e88092983acbc292b203b2"
    },
    {
        "nom": "Théorie socioculturelle de Vygotsky",
        "resume": (
            "L'apprentissage se produit dans la zone proximale de développement (ZPD), "
            "l'espace entre ce que l'apprenant peut faire seul et ce qu'il peut faire avec "
            "aide (Vygotsky). L'interaction sociale et l'étayage d'un pair ou d'un adulte "
            "sont moteurs du développement."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e88090901cfc867ecfb2e9"
    },
    {
        "nom": "La Théorie Tripolaire de la Formation",
        "resume": (
            "La formation résulte de trois pôles en tension : la relation à soi (autoformation), "
            "la relation aux autres (hétéroformation) et la relation aux choses/environnement "
            "(écoformation). L'éducation à la nature concerne particulièrement le troisième "
            "pôle : se laisser former par le contact avec le vivant."
        ),
        "notion_url": "https://www.notion.so/22957d3941e880b1a546ec9aa69cf9cd"
    },
    {
        "nom": "L'apprentissage situé",
        "resume": (
            "L'apprentissage est inséparable de son contexte (Lave & Wenger). On apprend "
            "en participant à une communauté de pratique dans un environnement authentique. "
            "Les connaissances acquises in situ sont plus transférables car elles sont "
            "ancrées dans des situations réelles."
        ),
        "notion_url": "https://www.notion.so/23c57d3941e880eb8588ff1ddd5a6d48"
    },
    {
        "nom": "La théorie des systèmes dynamiques en apprentissage",
        "resume": (
            "L'apprentissage est un processus non-linéaire et auto-organisé, sensible aux "
            "conditions initiales. Les progrès se font par paliers avec des périodes de "
            "plateau. L'environnement riche et varié favorise l'émergence de nouveaux "
            "comportements et compréhensions."
        ),
        "notion_url": "https://www.notion.so/22957d3941e880aeb0dfde3e60848f19"
    },
    {
        "nom": "L'apprentissage incarné",
        "resume": (
            "Le corps, les sens et le mouvement sont des vecteurs fondamentaux de "
            "connaissance (Varela, Merleau-Ponty). L'esprit n'est pas séparé du corps. "
            "Les activités sensorielles, motrices et émotionnelles en plein air s'inscrivent "
            "directement dans cette théorie."
        ),
        "notion_url": "https://www.notion.so/22957d3941e8809daca0d36626b989ef"
    },
]

# =============================================================================
# DONNÉES : CYCLES SCOLAIRES
# =============================================================================

CYCLES = [
    {"nom": "Cycle 1", "code": "C1", "ages": "3-6 ans (Maternelle)"},
    {"nom": "Cycle 2", "code": "C2", "ages": "6-9 ans (CP, CE1, CE2)"},
    {"nom": "Cycle 3", "code": "C3", "ages": "9-12 ans (CM1, CM2, 6ème)"},
    {"nom": "Cycle 4", "code": "C4", "ages": "12-15 ans (5ème, 4ème, 3ème)"},
]

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("IMPORT PÉDAGOGIES, THÉORIES & CYCLES -> SQLITE")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERREUR : Base SQLite introuvable : {DB_PATH}")
        print("   Lancez d'abord create_schema.py")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    # Pédagogies
    print("\n Import des pédagogies...")
    p_inserted = 0
    for p in PEDAGOGIES:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO pedagogie (nom, resume, notion_url)
            VALUES (?, ?, ?)
        """, (p["nom"], p["resume"], p["notion_url"]))
        if cursor.rowcount > 0:
            p_inserted += 1
    print(f"  OK {p_inserted} pédagogie(s) insérée(s) ({len(PEDAGOGIES)} au total)")

    # Théories
    print("\n Import des théories d'apprentissage...")
    t_inserted = 0
    for t in THEORIES:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO theorie_apprentissage (nom, resume, notion_url)
            VALUES (?, ?, ?)
        """, (t["nom"], t["resume"], t["notion_url"]))
        if cursor.rowcount > 0:
            t_inserted += 1
    print(f"  OK {t_inserted} théorie(s) insérée(s) ({len(THEORIES)} au total)")

    # Cycles
    print("\n Import des cycles scolaires...")
    c_inserted = 0
    for c in CYCLES:
        cursor = conn.execute("""
            INSERT OR IGNORE INTO cycle (nom, code, ages)
            VALUES (?, ?, ?)
        """, (c["nom"], c["code"], c["ages"]))
        if cursor.rowcount > 0:
            c_inserted += 1
    print(f"  OK {c_inserted} cycle(s) inséré(s)")

    conn.commit()
    conn.close()

    print(f"\n{'=' * 60}")
    print("Import terminé.")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
