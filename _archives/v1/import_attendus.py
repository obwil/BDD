# =============================================================================
# import_attendus.py
# =============================================================================
# Peuple la table attendu_scolaire dans SQLite.
# Données hardcodées depuis le référentiel EDD (Éducation au Développement Durable).
# Idempotent : utilise INSERT OR IGNORE.
#
# Structure : (cycle_code, domaine, sous_domaine_code, libelle)
# cycle_code : C1, C2, C3, C4
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

# =============================================================================
# DONNÉES
# Format : (cycle_code, domaine, sous_domaine_code, libelle)
# =============================================================================

ATTENDUS = [

    # =========================================================================
    # CYCLE 1 — Maternelle (3-6 ans)
    # =========================================================================

    # Thème 1 — Biodiversité et écosystèmes
    ("C1", "Biodiversité et écosystèmes", "1.1",
     "Observer, nommer, décrire des êtres vivants et leurs interactions ; identifier étapes de développement"),
    ("C1", "Biodiversité et écosystèmes", "1.2",
     "Identifier interactions humain/vivant ; adopter des écogestes ; participer à une action de préservation"),
    ("C1", "Biodiversité et écosystèmes", "1.3",
     "Relier biodiversité et santé humaine ; exprimer des émotions au contact de la nature ; identifier besoins des animaux/végétaux"),

    # Thème 2 — Alimentation
    ("C1", "Alimentation", "2.1",
     "Observer la croissance des végétaux ; décrire les besoins d'une plante"),
    ("C1", "Alimentation", "2.2",
     "Décrire les saveurs ; prendre conscience du lien alimentation/santé"),
    ("C1", "Alimentation", "2.3",
     "Prendre conscience de l'impact des emballages ; trier les déchets alimentaires"),

    # Thème 3 — Eau et changement climatique
    ("C1", "Eau et changement climatique", "3.1",
     "Identifier la présence de l'eau dans l'environnement proche"),
    ("C1", "Eau et changement climatique", "3.2",
     "Observer et décrire les usages quotidiens de l'eau"),
    ("C1", "Eau et changement climatique", "3.3",
     "Adopter des écogestes pour limiter la consommation d'eau"),

    # Thème 4 — Gestion durable des ressources naturelles
    ("C1", "Gestion durable des ressources naturelles", "4.1",
     "Observer matières et matériaux naturels ; distinguer vivant/non-vivant"),
    ("C1", "Gestion durable des ressources naturelles", "4.2",
     "Manipuler et transformer des matières ; identifier des risques liés aux ressources"),
    ("C1", "Gestion durable des ressources naturelles", "4.3",
     "S'interroger sur les gestes du quotidien (eau, énergie) ; adopter des écogestes"),

    # Thème 5 — Aménagement durable des territoires
    ("C1", "Aménagement durable des territoires", "5.1",
     "Observer l'environnement urbain et ses constructions ; suivre les changements saisonniers"),
    ("C1", "Aménagement durable des territoires", "5.2",
     "Identifier des risques environnementaux (naturels, technologiques) ; adopter des gestes de protection"),
    ("C1", "Aménagement durable des territoires", "5.3",
     "Découvrir les modes de déplacement ; développer des déplacements actifs"),

    # Thème 6 — Numérique
    ("C1", "Numérique", "6.1",
     "Identifier des outils numériques pour décrire l'environnement"),
    ("C1", "Numérique", "6.2",
     "Prendre conscience des effets des écrans sur la santé"),
    ("C1", "Numérique", "6.3",
     "Comprendre que les objets numériques peuvent être réparés, recyclés"),

    # =========================================================================
    # CYCLE 2 — CP, CE1, CE2 (6-9 ans)
    # =========================================================================

    # Thème 1 — Biodiversité et écosystèmes
    ("C2", "Biodiversité et écosystèmes", "1.1",
     "Observer, nommer, décrire et comparer des êtres vivants ; identifier interactions vivant/milieu ; mener une investigation scientifique"),
    ("C2", "Biodiversité et écosystèmes", "1.2",
     "Expliquer des impacts des actions humaines sur la biodiversité ; proposer des actions de préservation ; participer à un choix collectif"),
    ("C2", "Biodiversité et écosystèmes", "1.3",
     "Identifier des liens biodiversité/santé par investigation ; mettre en œuvre des écogestes favorables à la santé des humains et du vivant"),

    # Thème 2 — Alimentation
    ("C2", "Alimentation", "2.1",
     "Comparer des modes de production agricole et leurs impacts ; représenter des relations alimentaires (chaînes, réseaux) ; étudier des régimes alimentaires"),
    ("C2", "Alimentation", "2.2",
     "Établir des liens alimentation/santé ; pratiquer une démarche d'investigation sur l'équilibre alimentaire"),
    ("C2", "Alimentation", "2.3",
     "Identifier les fruits/légumes de saison ; expliquer l'intérêt des circuits courts ; réduire les déchets alimentaires"),

    # Thème 3 — Eau et changement climatique
    ("C2", "Eau et changement climatique", "3.1",
     "Comparer les états de l'eau par expériences ; relier phénomènes météorologiques et cycle de l'eau ; identifier les réservoirs d'eau"),
    ("C2", "Eau et changement climatique", "3.2",
     "Décrire les usages quotidiens de l'eau ; expliquer les incidences de son comportement sur la disponibilité et la qualité de l'eau"),
    ("C2", "Eau et changement climatique", "3.3",
     "Imaginer des solutions contre le gaspillage ; participer à une action concrète de gestion raisonnée à l'école"),

    # Thème 4 — Gestion durable des ressources naturelles
    ("C2", "Gestion durable des ressources naturelles", "4.1",
     "Différencier intérêt particulier et intérêt général ; être sensibilisé à l'impact de ses consommations (papier, alimentation)"),
    ("C2", "Gestion durable des ressources naturelles", "4.2",
     "Identifier des liens alimentation/besoins/ressources ; comparer l'exploitation des ressources selon les territoires ; comprendre des relations mode de vie/ressources"),
    ("C2", "Gestion durable des ressources naturelles", "4.3",
     "Mesurer l'impact des actions individuelles sur les déchets ; imaginer et mettre en œuvre des actions de réduction du gaspillage ; appliquer des écogestes à l'école"),

    # Thème 5 — Aménagement durable des territoires
    ("C2", "Aménagement durable des territoires", "5.1",
     "Identifier des aménagements durables dans sa commune ; comprendre le rôle des acteurs locaux ; participer à une action d'aménagement"),
    ("C2", "Aménagement durable des territoires", "5.2",
     "Identifier des équipements d'adaptation aux risques climatiques ; comparer des paysages passés/présents en lien avec les risques"),
    ("C2", "Aménagement durable des territoires", "5.3",
     "Être sensibilisé aux incidences du mode de déplacement sur la santé ; pratiquer des mobilités actives"),

    # Thème 6 — Numérique
    ("C2", "Numérique", "6.1",
     "Pratiquer une première démarche d'investigation avec des outils numériques ; être sensibilisé à un usage critique d'Internet"),
    ("C2", "Numérique", "6.2",
     "Distinguer intérêt particulier et comportement responsable face aux écrans ; prendre conscience des effets sur la santé (sommeil, vue, sédentarité)"),
    ("C2", "Numérique", "6.3",
     "Identifier des impacts environnementaux du numérique ; adopter des écogestes (réparer, recycler)"),

    # =========================================================================
    # CYCLE 3 — CM1, CM2, 6e (9-12 ans)
    # =========================================================================

    # Thème 1 — Biodiversité et écosystèmes
    ("C3", "Biodiversité et écosystèmes", "1.1",
     "Décrire la diversité du vivant à différentes échelles ; construire un arbre de parenté ; utiliser des clés de détermination ; pratiquer une démarche d'investigation sur la biodiversité ; exprimer la relation humain/nature"),
    ("C3", "Biodiversité et écosystèmes", "1.2",
     "Caractériser l'érosion de la biodiversité dans le temps (temps géologiques + histoire humaine) ; identifier des enjeux et acteurs de préservation ; participer à un débat et à des actions dépassant le cadre de l'école"),
    ("C3", "Biodiversité et écosystèmes", "1.3",
     "Évaluer l'impact des pratiques agricoles sur la biodiversité et la santé (humaine, animale, écosystémique) ; distinguer connaissance scientifique et opinion ; relier consommation locale/durable et santé"),

    # Thème 2 — Alimentation
    ("C3", "Alimentation", "2.1",
     "Identifier des systèmes agricoles et leurs impacts ; expliquer le rôle des pollinisateurs, des décomposeurs, des végétaux dans la production de matière ; reconnaître les aliments ultra-transformés ; relier production alimentaire et ODD"),
    ("C3", "Alimentation", "2.2",
     "Expliquer le rôle des aliments dans l'organisme ; comprendre les risques sanitaires et méthodes de conservation ; distinguer connaissance scientifique, croyance et opinion sur l'alimentation"),
    ("C3", "Alimentation", "2.3",
     "Proposer des solutions concrètes contre le gaspillage alimentaire à l'échelle de l'école et de la commune ; justifier des écogestes alimentaires par un argumentaire"),

    # Thème 3 — Eau et changement climatique
    ("C3", "Eau et changement climatique", "3.1",
     "Représenter et expliquer le cycle de l'eau comme système ; différencier météo et climat ; relier changement climatique et cycle de l'eau"),
    ("C3", "Eau et changement climatique", "3.2",
     "Relier cycle de l'eau et usages humains ; repérer des inégalités mondiales d'accès à l'eau ; identifier des conflits d'usages ; appréhender l'eau comme bien commun"),
    ("C3", "Eau et changement climatique", "3.3",
     "Identifier des acteurs locaux de la gestion de l'eau ; proposer des actions dépassant le cadre de l'école ; mobiliser les valeurs de solidarité, équité, justice"),

    # Thème 4 — Gestion durable des ressources naturelles
    ("C3", "Gestion durable des ressources naturelles", "4.1",
     "Caractériser différents types de ressources ; distinguer renouvelables et non renouvelables par une démarche d'investigation"),
    ("C3", "Gestion durable des ressources naturelles", "4.2",
     "Représenter des consommations (énergie, eau, sol) par schémas/diagrammes ; expliquer les effets de l'exploitation sur l'environnement ; justifier une gestion raisonnée"),
    ("C3", "Gestion durable des ressources naturelles", "4.3",
     "Repérer des tensions entre enjeux éthiques, environnementaux et sociaux liés aux ressources ; participer à une action collective de consommation raisonnée ; justifier des écogestes"),

    # Thème 5 — Aménagement durable des territoires
    ("C3", "Aménagement durable des territoires", "5.1",
     "Analyser les paysages urbains ; identifier le rôle de l'urbanisation dans le changement climatique ; identifier des stratégies d'atténuation/adaptation en ville ; imaginer la ville de demain (maquettes, schémas)"),
    ("C3", "Aménagement durable des territoires", "5.2",
     "Connaître les risques naturels liés à l'activité terrestre ; différencier risques climatiques et non climatiques ; expliquer la vulnérabilité des littoraux ; participer à une action concrète de réduction des risques"),
    ("C3", "Aménagement durable des territoires", "5.3",
     "Analyser des besoins de mobilité ; comparer les impacts des modes de déplacement sur la santé et l'environnement ; identifier et justifier un transport durable"),

    # Thème 6 — Numérique
    ("C3", "Numérique", "6.1",
     "Pratiquer une démarche d'investigation sur un enjeu EDD avec des outils numériques ; estimer son empreinte carbone ; distinguer connaissance et opinion ; développer l'esprit critique face aux sources"),
    ("C3", "Numérique", "6.2",
     "Identifier des enjeux de citoyenneté et de santé liés au numérique ; adopter des comportements responsables en ligne"),
    ("C3", "Numérique", "6.3",
     "Estimer l'empreinte carbone d'objets numériques ; s'engager dans des actions écoresponsables liées au numérique ; s'approprier la notion de sobriété numérique"),

    # =========================================================================
    # CYCLE 4 — 5e, 4e, 3e (11-15 ans)
    # =========================================================================

    # Thème 1 — Biodiversité et écosystèmes
    ("C4", "Biodiversité et écosystèmes", "1.1",
     "Identifier et expliquer les interactions entre êtres vivants ; utiliser des outils d'identification et de classification ; mener des démarches d'investigation sur le fonctionnement des écosystèmes ; décrire les rapports humains/biodiversité"),
    ("C4", "Biodiversité et écosystèmes", "1.2",
     "Identifier les impacts humains sur la biodiversité ; évaluer son érosion par démarche scientifique ; distinguer les échelles d'action politique (local->global) ; proposer des actions de préservation"),
    ("C4", "Biodiversité et écosystèmes", "1.3",
     "Relier destruction des écosystèmes et émergence de maladies infectieuses (approche One Health) ; comprendre le rôle du microbiome ; identifier le rôle des pollinisateurs ; mesurer l'impact humain sur l'antibiorésistance"),

    # Thème 2 — Alimentation
    ("C4", "Alimentation", "2.1",
     "Comparer systèmes agricoles (intensif, agroécologie, pêche…) ; relier pratiques agricoles et impacts environnementaux (sols, biodiversité, climat) ; envisager des avenirs durables pour nourrir le monde"),
    ("C4", "Alimentation", "2.2",
     "Définir la sécurité alimentaire ; relier alimentation, polluants et santé (One Health) ; distinguer savoirs scientifiques d'opinions sur les effets alimentaires"),
    ("C4", "Alimentation", "2.3",
     "Déterminer des critères de consommation responsable (local, saison, durable) ; justifier des choix alimentaires pour la protection de l'environnement ; identifier écogestes et leurs limites"),

    # Thème 3 — Eau et changement climatique
    ("C4", "Eau et changement climatique", "3.1",
     "Décrire les perturbations climatiques du cycle de l'eau (sécheresses, crues, fonte des glaces) ; mener des sciences participatives pour mesurer les impacts humains"),
    ("C4", "Eau et changement climatique", "3.2",
     "Analyser la disponibilité et la demande en eau douce ; identifier acteurs et responsabilités à différentes échelles ; relier usages de l'eau à la santé et aux écosystèmes"),
    ("C4", "Eau et changement climatique", "3.3",
     "Connaître l'ODD 6 (accès à l'eau et assainissement) ; proposer des mesures d'atténuation/adaptation ; débattre de choix de gestion (barrages, zones humides, assainissement…) ; développer des attitudes durables à l'échelle locale"),
]

# =============================================================================
# IMPORT
# =============================================================================

def main():
    print("=" * 60)
    print("IMPORT ATTENDUS SCOLAIRES -> SQLITE")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERREUR : Base SQLite introuvable : {DB_PATH}")
        print("   Lancez d'abord create_schema.py")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    # Construire un index cycle_code -> cycle_id
    cycles = conn.execute("SELECT id, code FROM cycle").fetchall()
    cycle_map = {row[1]: row[0] for row in cycles}

    if not cycle_map:
        print("ERREUR : Aucun cycle en base. Lancez d'abord import_pedagogies.py")
        conn.close()
        return

    print(f"\n  Cycles trouvés : {cycle_map}")
    print(f"\n  {len(ATTENDUS)} attendus à importer...\n")

    inserted = 0
    skipped = 0

    for (cycle_code, domaine, sous_domaine_code, libelle) in ATTENDUS:
        cycle_id = cycle_map.get(cycle_code)
        if not cycle_id:
            print(f"  AVERTISSEMENT : cycle '{cycle_code}' inconnu — ligne ignorée")
            skipped += 1
            continue

        cursor = conn.execute("""
            INSERT OR IGNORE INTO attendu_scolaire (cycle_id, domaine, sous_domaine, libelle)
            VALUES (?, ?, ?, ?)
        """, (cycle_id, domaine, sous_domaine_code, libelle))

        if cursor.rowcount > 0:
            inserted += 1
        else:
            skipped += 1

    conn.commit()
    conn.close()

    print(f"  OK : {inserted} attendu(s) inséré(s), {skipped} ignoré(s) (déjà présents)")
    print(f"\n{'=' * 60}")
    print("Import terminé.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
