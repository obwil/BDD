# =============================================================================
# import_attendus_disciplinaires.py
# =============================================================================
# Peuple la table attendu_scolaire avec les attendus disciplinaires (hors EDD).
# Donnees hardcodees depuis le referentiel programmatique (BO) pour C1, C2, C3.
# Idempotent : utilise INSERT OR IGNORE.
#
# Prerequis : avoir lance migration_ajout_type_attendu.py
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

# =============================================================================
# DONNEES
# Format : (cycle_code, domaine, sous_domaine, libelle, type)
# =============================================================================

ATTENDUS = [

    # =========================================================================
    # CYCLE 1 — Maternelle (3-6 ans)
    # =========================================================================

    ("C1", "Explorer le monde - Monde vivant", "5.2",
     "Identifier, nommer et regrouper des animaux selon leurs caracteristiques (tegument, modes de deplacement, milieux de vie)",
     "disciplinaire"),
    ("C1", "Explorer le monde - Monde vivant", "5.2",
     "Observer et decrire les principales etapes du developpement d'un animal ou d'un vegetal via elevages et plantations",
     "disciplinaire"),
    ("C1", "Explorer le monde - Monde vivant", "5.2",
     "Connaitre les besoins essentiels de quelques animaux et vegetaux",
     "disciplinaire"),
    ("C1", "Explorer le monde - Monde vivant", "5.2",
     "Developper les aptitudes sensorielles (olfactif, gustatif, tactile, auditif, visuel) pour distinguer et decrire des realites naturelles",
     "disciplinaire"),
    ("C1", "Explorer le monde - Monde vivant", "5.2",
     "Explorer les matieres naturelles par action directe : eau, bois, terre, sable, air (transvaser, malaxer, melanger, modeler, transformer)",
     "disciplinaire"),
    ("C1", "Explorer le monde - Espace", "5.1",
     "Observer l'environnement immediat lors de sorties en milieu naturel ; produire des images et amorcer une attitude responsable (respect des lieux et du vivant)",
     "disciplinaire"),
    ("C1", "Mobiliser le langage - Oral", "1.1",
     "Utiliser l'observation du vivant et des matieres naturelles comme support de description orale et d'enrichissement du vocabulaire",
     "disciplinaire"),
    ("C1", "Activite physique", "2.1",
     "Se deplacer avec aisance et en securite dans des environnements varies naturels ou peu familiers (foret, parc, terrain irregulier)",
     "disciplinaire"),

    # =========================================================================
    # CYCLE 2 — CP, CE1, CE2 (6-9 ans)
    # =========================================================================

    ("C2", "Questionner le monde - Monde vivant", None,
     "Identifier ce qui est animal, vegetal, mineral ou elabore par des etres vivants",
     "disciplinaire"),
    ("C2", "Questionner le monde - Monde vivant", None,
     "Connaitre le developpement des animaux et des vegetaux et leur cycle de vie (naissance, croissance, reproduction, mort)",
     "disciplinaire"),
    ("C2", "Questionner le monde - Monde vivant", None,
     "Connaitre les regimes alimentaires de quelques animaux et les besoins vitaux des vegetaux",
     "disciplinaire"),
    ("C2", "Questionner le monde - Monde vivant", None,
     "Identifier la diversite des organismes vivants presents dans un milieu et leur interdependance",
     "disciplinaire"),
    ("C2", "Questionner le monde - Monde vivant", None,
     "Connaitre les relations alimentaires entre organismes vivants et les chaines de predation ; realiser des schemas simples",
     "disciplinaire"),
    ("C2", "Questionner le monde - Monde vivant", None,
     "Realiser de petits ecosystemes en classe ou a l'ecole : elevages, cultures, jardin d'ecole, mare d'ecole",
     "disciplinaire"),
    ("C2", "Questionner le monde - Matiere et phenomenes naturels", None,
     "Reconnaitre les etats de l'eau et leur manifestation dans des phenomenes naturels observables : pluie, neige, grele, glace, nuages, cours d'eau",
     "disciplinaire"),
    ("C2", "Questionner le monde - Matiere et phenomenes naturels", None,
     "Prendre conscience de l'existence et de quelques proprietes de l'air (materialite, effets du vent) a travers des experiences simples",
     "disciplinaire"),
    ("C2", "Questionner le monde - Espace", None,
     "Observer et decrire des espaces proches lors de sorties de terrain ; produire des representations simples de l'environnement proche",
     "disciplinaire"),
    ("C2", "Education physique et sportive", None,
     "Adapter ses deplacements a des environnements varies, peu familiers ou naturels : randonnee, parcours d'orientation, activites de pleine nature",
     "disciplinaire"),
    ("C2", "Education physique et sportive", None,
     "Lire le milieu et adapter ses deplacements a ses contraintes ; reconnaitre une situation a risque",
     "disciplinaire"),
    ("C2", "Francais", None,
     "Utiliser les observations du vivant et de la matiere comme support de description orale et ecrite, d'enrichissement du vocabulaire specifique",
     "disciplinaire"),
    ("C2", "Francais", None,
     "Rediger des comptes rendus d'experience ou d'observation (ecrits courts integres aux sequences Questionner le monde)",
     "disciplinaire"),
    ("C2", "Arts plastiques", None,
     "Representer l'environnement proche par le dessin (carnet de croquis, observation in situ) ; explorer la representation de matieres naturelles",
     "disciplinaire"),
    ("C2", "Enseignement moral et civique", None,
     "Sensibilisation aux biens communs : ressources naturelles, biodiversite (initiation au developpement durable)",
     "disciplinaire"),

    # =========================================================================
    # CYCLE 3 — CM1, CM2, 6e (9-12 ans)
    # =========================================================================

    # Classification
    ("C3", "Sciences et technologie - Le vivant", "Classification",
     "Distinguer les differents niveaux d'organisation du vivant (organisme, appareil, organe) a partir d'exemples de plantes et d'animaux",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Classification",
     "Realiser une classification en groupes embotes pour mettre en evidence des liens de parente a partir d'especes observees",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Classification",
     "Determiner des especes biologiques de l'environnement proche en utilisant une cle de determination",
     "disciplinaire"),

    # Biodiversite
    ("C3", "Sciences et technologie - Le vivant", "Biodiversite",
     "Caracteriser le changement de la biodiversite au cours de l'histoire de la Terre (fossiles, echelle des temps geologiques)",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Biodiversite",
     "Placer plusieurs especes actuelles et fossiles sur une echelle des temps",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Biodiversite",
     "Exploiter des documents pour mettre en evidence l'existence de grandes crises biologiques",
     "disciplinaire"),

    # Cycle de vie
    ("C3", "Sciences et technologie - Le vivant", "Cycle de vie",
     "Exploiter des observations issues de cultures ou d'elevages pour identifier les etapes d'un cycle de vie",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Cycle de vie",
     "Mettre en evidence le role de la pollinisation dans la transformation de la fleur en fruit et des ovules en graines",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Cycle de vie",
     "Illustrer la notion de cooperation mutualiste avec l'exemple de la pollinisation",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Cycle de vie",
     "Relier l'evolution de l'abondance des pollinisateurs a ses consequences sur les cultures",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Cycle de vie",
     "Comprendre l'impact de l'utilisation des pesticides sur les pollinisateurs",
     "disciplinaire"),

    # Ecosystemes
    ("C3", "Sciences et technologie - Le vivant", "Ecosystemes",
     "Caracteriser un ecosysteme par son milieu de vie, l'ensemble des etres vivants et les interactions en son sein",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Ecosystemes",
     "Decrire plusieurs types de relations entre especes : cooperations, predation, etc.",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Ecosystemes",
     "Comparer la repartition des etres vivants dans des milieux proches en lien avec les facteurs abiotiques : temperature, ensoleillement, humidite",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Ecosystemes",
     "Mettre en evidence la place et l'interdependance des etres vivants dans un reseau trophique",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Ecosystemes",
     "Decrire et interpreter les composantes biologiques, geologiques et anthropiques d'un paysage local a partir d'une sortie sur le terrain (6e)",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Ecosystemes",
     "Caracteriser les consequences d'une action humaine sur un ecosysteme",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Le vivant", "Ecosystemes",
     "Pratiquer des sciences participatives liees aux milieux naturels (ex. Vigie-Nature Ecole)",
     "disciplinaire"),

    # Meteorologie et climat
    ("C3", "Sciences et technologie - La Terre", "Meteorologie et climat",
     "Distinguer la meteorologie du climat",
     "disciplinaire"),
    ("C3", "Sciences et technologie - La Terre", "Meteorologie et climat",
     "Realiser et exploiter des mesures meteorologiques locales a l'aide de capteurs : thermometre, pluviometre, anemometre",
     "disciplinaire"),
    ("C3", "Sciences et technologie - La Terre", "Meteorologie et climat",
     "Relier le rechauffement climatique a l'evolution des gaz a effet de serre et decrire ses consequences sur le peuplement des milieux",
     "disciplinaire"),
    ("C3", "Sciences et technologie - La Terre", "Meteorologie et climat",
     "Citer des strategies d'attenuation ou d'adaptation au rechauffement climatique",
     "disciplinaire"),

    # Ressources naturelles et risques
    ("C3", "Sciences et technologie - La Terre", "Ressources naturelles et risques",
     "Identifier des ressources naturelles exploitees par les societes humaines en lien avec l'activite de la Terre",
     "disciplinaire"),
    ("C3", "Sciences et technologie - La Terre", "Ressources naturelles et risques",
     "Identifier un risque naturel a partir d'un exemple local (erosion littorale, inondation) et les modalites de prevention associees",
     "disciplinaire"),

    # Matiere
    ("C3", "Sciences et technologie - Matiere", None,
     "Distinguer les materiaux fabriques ou transformes par l'etre humain des materiaux directement disponibles dans la nature",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Matiere", None,
     "Rechercher des informations sur la duree de decomposition de materiaux dans la nature pour en identifier les consequences environnementales",
     "disciplinaire"),
    ("C3", "Sciences et technologie - Matiere", None,
     "Separer les constituants d'un melange (tamisage, decantation, filtration) - application : eau, sol, litiere forestiere",
     "disciplinaire"),

    # EPS
    ("C3", "Education physique et sportive", None,
     "Adapter ses deplacements a des environnements naturels varies : randonnee, parcours d'orientation, activites de pleine nature",
     "disciplinaire"),
    ("C3", "Education physique et sportive", None,
     "Lire le milieu, adapter ses deplacements a ses contraintes et reconnaitre une situation a risque",
     "disciplinaire"),

    # Francais
    ("C3", "Francais", None,
     "Utiliser les observations du vivant comme support de descriptions orales et ecrites de plus en plus precises et structurees",
     "disciplinaire"),
    ("C3", "Francais", None,
     "Rediger des comptes rendus d'experience ou d'investigation scientifique (ecrits de travail, syntheses, schemas legendes)",
     "disciplinaire"),
    ("C3", "Francais", None,
     "Lire et exploiter des textes documentaires illustres sur le monde vivant",
     "disciplinaire"),

    # Histoire et geographie
    ("C3", "Histoire et geographie", None,
     "Identifier des paysages naturels et leurs caracteristiques a differentes echelles",
     "disciplinaire"),
    ("C3", "Histoire et geographie", None,
     "Identifier quelques interactions elementaires entre modes de vie humains et environnement naturel (alimentation, habitat, deplacements)",
     "disciplinaire"),
    ("C3", "Histoire et geographie", None,
     "Comparer des paysages d'aujourd'hui et du passe pour mettre en evidence des transformations liees aux activites humaines",
     "disciplinaire"),
]

# =============================================================================
# IMPORT
# =============================================================================

def main():
    print("=" * 60)
    print("IMPORT ATTENDUS DISCIPLINAIRES -> SQLITE")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERREUR : Base SQLite introuvable : {DB_PATH}")
        print("   Lancez d'abord create_schema.py")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    # Verifier que la colonne type existe
    cols = [row[1] for row in conn.execute("PRAGMA table_info(attendu_scolaire)").fetchall()]
    if "type" not in cols:
        print("ERREUR : colonne 'type' absente. Lancez d'abord migration_ajout_type_attendu.py")
        conn.close()
        return

    # Construire un index cycle_code -> cycle_id
    cycles = conn.execute("SELECT id, code FROM cycle").fetchall()
    cycle_map = {row[1]: row[0] for row in cycles}

    if not cycle_map:
        print("ERREUR : Aucun cycle en base. Lancez d'abord import_pedagogies.py")
        conn.close()
        return

    print(f"\n  Cycles trouves : {cycle_map}")
    print(f"\n  {len(ATTENDUS)} attendus a importer...\n")

    inserted = 0
    skipped = 0

    for (cycle_code, domaine, sous_domaine, libelle, type_val) in ATTENDUS:
        cycle_id = cycle_map.get(cycle_code)
        if not cycle_id:
            print(f"  AVERTISSEMENT : cycle '{cycle_code}' inconnu — ligne ignoree")
            skipped += 1
            continue

        cursor = conn.execute("""
            INSERT OR IGNORE INTO attendu_scolaire (cycle_id, domaine, sous_domaine, libelle, type)
            VALUES (?, ?, ?, ?, ?)
        """, (cycle_id, domaine, sous_domaine, libelle, type_val))

        if cursor.rowcount > 0:
            inserted += 1
        else:
            skipped += 1

    conn.commit()
    conn.close()

    print(f"  OK : {inserted} attendu(s) insere(s), {skipped} ignore(s) (deja presents)")
    print(f"\n{'=' * 60}")
    print("Import termine.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
