# =============================================================================
# import_classification.py
# =============================================================================
# Peuple les tables thematique et objectif dans SQLite.
# Données hardcodées — aucune dépendance à un fichier externe.
# Idempotent : utilise INSERT OR IGNORE.
#
# Format : liste de tuples (nom, niveau, nom_parent ou None)
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

# =============================================================================
# CLASSIFICATION THÉMATIQUE
# =============================================================================

THEMATIQUES = [
    # Biosphère
    ("Biosphère", 0, None),
      ("Evolution", 1, "Biosphère"),
      ("Taxonomie", 1, "Biosphère"),
        ("Phylogénie", 2, "Taxonomie"),
          ("Rangs taxonomiques", 3, "Phylogénie"),
            ("Espèce", 4, "Rangs taxonomiques"),
            ("Genre", 4, "Rangs taxonomiques"),
            ("Famille", 4, "Rangs taxonomiques"),
            ("Ordre", 4, "Rangs taxonomiques"),
            ("Classe", 4, "Rangs taxonomiques"),
            ("Embranchement", 4, "Rangs taxonomiques"),
            ("Règne", 4, "Rangs taxonomiques"),
      ("Caractéristiques des êtres vivants", 1, "Biosphère"),
        ("Naissance", 2, "Caractéristiques des êtres vivants"),
        ("Nourrissage", 2, "Caractéristiques des êtres vivants"),
        ("Développement", 2, "Caractéristiques des êtres vivants"),
        ("Reproduction", 2, "Caractéristiques des êtres vivants"),
        ("Mort", 2, "Caractéristiques des êtres vivants"),
      ("Règne animal", 1, "Biosphère"),
        ("Groupes animaux", 2, "Règne animal"),
          ("Arthropodes", 3, "Groupes animaux"),
            ("Insectes", 4, "Arthropodes"),
            ("Arachnides", 4, "Arthropodes"),
            ("Crustacés", 4, "Arthropodes"),
            ("Myriapodes", 4, "Arthropodes"),
          ("Mammifères", 3, "Groupes animaux"),
          ("Oiseaux", 3, "Groupes animaux"),
          ("Amphibiens", 3, "Groupes animaux"),
          ("Poissons", 3, "Groupes animaux"),
          ("Reptiles", 3, "Groupes animaux"),
          ("Annélides", 3, "Groupes animaux"),
            ("Lombrics", 4, "Annélides"),
          ("Mollusques", 3, "Groupes animaux"),
          ("Echinodermes", 3, "Groupes animaux"),
          ("Vers plats", 3, "Groupes animaux"),
          ("Nématodes", 3, "Groupes animaux"),
        ("Ethologie", 2, "Règne animal"),
          ("Déplacement animal", 3, "Ethologie"),
          ("Communication animale", 3, "Ethologie"),
          ("Abris", 3, "Ethologie"),
          ("Stratégie de survie", 3, "Ethologie"),
      ("Règne végétal", 1, "Biosphère"),
        ("Strates", 2, "Règne végétal"),
          ("Strate muscinale", 3, "Strates"),
          ("Strate herbacée", 3, "Strates"),
          ("Strate arbustive", 3, "Strates"),
          ("Strate arborée", 3, "Strates"),
          ("Strate aquatique", 3, "Strates"),
        ("Groupes végétaux", 2, "Règne végétal"),
          ("Angiospermes", 3, "Groupes végétaux"),
          ("Gymnospermes", 3, "Groupes végétaux"),
          ("Ptéridophytes", 3, "Groupes végétaux"),
          ("Bryophytes", 3, "Groupes végétaux"),
        ("Anatomie végétale", 2, "Règne végétal"),
          ("Fleur", 3, "Anatomie végétale"),
          ("Feuille", 3, "Anatomie végétale"),
          ("Fruit", 3, "Anatomie végétale"),
          ("Sève", 3, "Anatomie végétale"),
          ("Tige", 3, "Anatomie végétale"),
            ("Tige creuse", 4, "Tige"),
          ("Racine", 3, "Anatomie végétale"),
          ("Ecorce", 3, "Anatomie végétale"),
        ("Comportement végétal", 2, "Règne végétal"),
          ("Dispersion végétale", 3, "Comportement végétal"),
      ("Champignons", 1, "Biosphère"),
        ("Anatomie des champignons", 2, "Champignons"),
          ("Chapeau", 3, "Anatomie des champignons"),
          ("Pied", 3, "Anatomie des champignons"),
          ("Mycélium", 3, "Anatomie des champignons"),
        ("Spores", 2, "Champignons"),
        ("Mycorhizes", 2, "Champignons"),
        ("Lichens", 2, "Champignons"),
        ("Saprophytes", 2, "Champignons"),

    # Lithosphère
    ("Lithosphère", 0, None),
      ("Minéraux", 1, "Lithosphère"),
      ("Roches", 1, "Lithosphère"),
        ("Sédimentaire", 2, "Roches"),
        ("Magmatique", 2, "Roches"),
        ("Métamorphique", 2, "Roches"),
      ("Relief", 1, "Lithosphère"),
      ("Erosion", 1, "Lithosphère"),
      ("Tectonique des plaques", 1, "Lithosphère"),

    # Atmosphère
    ("Atmosphère", 0, None),
      ("Climat", 1, "Atmosphère"),
        ("Changement climatique", 2, "Climat"),
          ("Naturel", 3, "Changement climatique"),
          ("Anthropique", 3, "Changement climatique"),
        ("Types de climat", 2, "Climat"),
          ("Tempéré", 3, "Types de climat"),
          ("Continental", 3, "Types de climat"),
          ("Océanique", 3, "Types de climat"),
          ("Méditerranéen", 3, "Types de climat"),
          ("Montagnard", 3, "Types de climat"),
      ("Paramètres météo", 1, "Atmosphère"),
        ("Pression", 2, "Paramètres météo"),
        ("Température", 2, "Paramètres météo"),
        ("Humidité", 2, "Paramètres météo"),
      ("Phénomènes météorologiques", 1, "Atmosphère"),
        ("Phénomènes d'air", 2, "Phénomènes météorologiques"),
          ("Vent", 3, "Phénomènes d'air"),
          ("Tempête", 3, "Phénomènes d'air"),
          ("Tornado", 3, "Phénomènes d'air"),
        ("Phénomènes électriques", 2, "Phénomènes météorologiques"),
          ("Orage", 3, "Phénomènes électriques"),
          ("Foudre", 3, "Phénomènes électriques"),
        ("Phénomènes lumineux", 2, "Phénomènes météorologiques"),
          ("Arc-en-ciel", 3, "Phénomènes lumineux"),
          ("Halo lunaire", 3, "Phénomènes lumineux"),
        ("Phénomènes d'eau", 2, "Phénomènes météorologiques"),
          ("Pluie", 3, "Phénomènes d'eau"),
          ("Neige", 3, "Phénomènes d'eau"),
          ("Grêle", 3, "Phénomènes d'eau"),
          ("Brouillard", 3, "Phénomènes d'eau"),
          ("Rosée", 3, "Phénomènes d'eau"),
          ("Givre", 3, "Phénomènes d'eau"),

    # Cohésion sociale
    ("Cohésion sociale", 0, None),
      ("Cultures", 1, "Cohésion sociale"),
      ("Handicap", 1, "Cohésion sociale"),
      ("Gastronomie", 1, "Cohésion sociale"),
      ("Musique du monde", 1, "Cohésion sociale"),
      ("Patrimoine", 1, "Cohésion sociale"),
      ("Représentation de la nature", 1, "Cohésion sociale"),
        ("Celtes", 2, "Représentation de la nature"),
        ("Mythologie grecque", 2, "Représentation de la nature"),
      ("Jeux coopératifs", 1, "Cohésion sociale"),
      ("Vivre ensemble", 1, "Cohésion sociale"),
      ("Citoyenneté", 1, "Cohésion sociale"),
      ("Traditions", 1, "Cohésion sociale"),

    # Biologie
    ("Biologie", 0, None),
      ("Physiologie", 1, "Biologie"),
      ("Chronobiologie", 1, "Biologie"),
      ("Système sensoriel", 1, "Biologie"),
        ("Vision", 2, "Système sensoriel"),
        ("Audition", 2, "Système sensoriel"),
        ("Chimioréception", 2, "Système sensoriel"),
        ("Gustation", 2, "Système sensoriel"),
        ("Olfaction", 2, "Système sensoriel"),
        ("Tactile", 2, "Système sensoriel"),
        ("Thermoréception", 2, "Système sensoriel"),
        ("Electroréception", 2, "Système sensoriel"),
        ("Proprioception", 2, "Système sensoriel"),
        ("Baroréception", 2, "Système sensoriel"),
        ("Hygroréception", 2, "Système sensoriel"),
        ("Nociception", 2, "Système sensoriel"),
        ("Magnétoréception", 2, "Système sensoriel"),
        ("Photoréception non-visuelle", 2, "Système sensoriel"),
        ("Graviréception", 2, "Système sensoriel"),
        ("Rhéoréception", 2, "Système sensoriel"),
        ("Echolocalisation", 2, "Système sensoriel"),
      ("Anatomie animale", 1, "Biologie"),
        ("Squelette", 2, "Anatomie animale"),
        ("Système nerveux", 2, "Anatomie animale"),
        ("Système respiratoire", 2, "Anatomie animale"),
        ("Système digestif", 2, "Anatomie animale"),
        ("Système circulatoire", 2, "Anatomie animale"),
      ("Biologie évolutive", 1, "Biologie"),
        ("Sélection naturelle", 2, "Biologie évolutive"),
        ("Adaptation", 2, "Biologie évolutive"),
        ("Spéciation", 2, "Biologie évolutive"),
        ("Extinction", 2, "Biologie évolutive"),
      ("Ecologie", 1, "Biologie"),
        ("Cycle de la matière", 2, "Ecologie"),
          ("Cycle de l'eau", 3, "Cycle de la matière"),
          ("Cycle du carbone", 3, "Cycle de la matière"),
          ("Cycle de l'azote", 3, "Cycle de la matière"),
          ("Cycle du phosphore", 3, "Cycle de la matière"),
        ("Ecologie du paysage", 2, "Ecologie"),
          ("Corridors biologiques", 3, "Ecologie du paysage"),
            ("Trame verte", 4, "Corridors biologiques"),
            ("Trame bleue", 4, "Corridors biologiques"),
            ("Trame noire", 4, "Corridors biologiques"),
            ("Trame blanche", 4, "Corridors biologiques"),
            ("Trame brune", 4, "Corridors biologiques"),
            ("Trame turquoise", 4, "Corridors biologiques"),
        ("Synécologie", 2, "Ecologie"),
          ("Ecosystèmes", 3, "Synécologie"),
            ("Forêt", 4, "Ecosystèmes"),
            ("Prairie", 4, "Ecosystèmes"),
            ("Champ", 4, "Ecosystèmes"),
            ("Mare", 4, "Ecosystèmes"),
            ("Rivière", 4, "Ecosystèmes"),
            ("Mer", 4, "Ecosystèmes"),
            ("Le sol", 4, "Ecosystèmes"),
            ("Arbre", 4, "Ecosystèmes"),
            ("Montagne", 4, "Ecosystèmes"),
            ("Haie", 4, "Ecosystèmes"),
          ("Interactions écologiques", 3, "Synécologie"),
            ("Pyramide alimentaire", 4, "Interactions écologiques"),
            ("Réseau trophique", 4, "Interactions écologiques"),
          ("Relations écologiques", 3, "Synécologie"),
            ("Amensalisme", 4, "Relations écologiques"),
            ("Commensalisme", 4, "Relations écologiques"),
            ("Parasitisme", 4, "Relations écologiques"),
            ("Prédation vraie", 4, "Relations écologiques"),
            ("Herbivorie", 4, "Relations écologiques"),
            ("Mutualisme", 4, "Relations écologiques"),
            ("Neutralisme", 4, "Relations écologiques"),
            ("Symbiose", 4, "Relations écologiques"),

    # Géophysique
    ("Géophysique", 0, None),
      ("Géophysique interne", 1, "Géophysique"),
        ("Géomagnétisme", 2, "Géophysique interne"),
      ("Géophysique des couches limites", 1, "Géophysique"),
      ("Géophysique externe", 1, "Géophysique"),

    # Astronomie
    ("Astronomie", 0, None),
      ("Planète Terre", 1, "Astronomie"),
        ("Orbite terrestre", 2, "Planète Terre"),
          ("Saisons", 3, "Orbite terrestre"),
            ("Printemps", 4, "Saisons"),
            ("Eté", 4, "Saisons"),
            ("Automne", 4, "Saisons"),
            ("Hiver", 4, "Saisons"),
        ("Rotation terrestre", 2, "Planète Terre"),
          ("Jour", 3, "Rotation terrestre"),
          ("Nuit", 3, "Rotation terrestre"),
        ("Système gravitationnel", 2, "Planète Terre"),
      ("Système solaire", 1, "Astronomie"),
      ("Galaxie", 1, "Astronomie"),
        ("Voie lactée", 2, "Galaxie"),
          ("Constellations", 3, "Voie lactée"),

    # Eléments abiotiques
    ("Eléments abiotiques", 0, None),
      ("L'eau", 1, "Eléments abiotiques"),
        ("Etats de l'eau", 2, "L'eau"),
      ("L'air", 1, "Eléments abiotiques"),
        ("Composition de l'air", 2, "L'air"),
          ("Dioxygène (O₂)", 3, "Composition de l'air"),
          ("Diazote (N₂)", 3, "Composition de l'air"),
          ("Dioxyde de carbone (CO₂)", 3, "Composition de l'air"),
          ("Vapeur d'eau", 3, "Composition de l'air"),
      ("Lumière", 1, "Eléments abiotiques"),
        ("Spectre visible", 2, "Lumière"),
        ("Ultraviolet", 2, "Lumière"),
        ("Infrarouge", 2, "Lumière"),

    # Réactions chimiques
    ("Réactions chimiques", 0, None),
      ("Combustion", 1, "Réactions chimiques"),
      ("Respiration cellulaire", 1, "Réactions chimiques"),
      ("Fermentation", 1, "Réactions chimiques"),
      ("Photosynthèse", 1, "Réactions chimiques"),

    # Bien-être
    ("Bien-être", 0, None),
      ("Motivation", 1, "Bien-être"),
      ("Estime de soi", 1, "Bien-être"),
      ("Activité physique", 1, "Bien-être"),
        ("Effort physique", 2, "Activité physique"),
          ("Marche", 3, "Effort physique"),
          ("Course", 3, "Effort physique"),
      ("Introspection", 1, "Bien-être"),
      ("Relaxation", 1, "Bien-être"),
      ("Méditation", 1, "Bien-être"),
      ("Alimentation saine", 1, "Bien-être"),
      ("Emotions", 1, "Bien-être"),

    # Applications interdisciplinaires
    ("Applications interdisciplinaires", 0, None),
      ("Conservation de la nature", 1, "Applications interdisciplinaires"),
        ("Protection des habitats", 2, "Conservation de la nature"),
          ("Restauration des écosystèmes dégradés", 3, "Protection des habitats"),
          ("Lutte contre la fragmentation des habitats", 3, "Protection des habitats"),
          ("Lutte contre la disparition des habitats", 3, "Protection des habitats"),
        ("Protection des espèces", 2, "Conservation de la nature"),
          ("Inventaire des espèces", 3, "Protection des espèces"),
          ("Disparition des espèces", 3, "Protection des espèces"),
        ("Suivi des écosystèmes", 2, "Conservation de la nature"),
          ("Espèces bioindicatrices", 3, "Suivi des écosystèmes"),
          ("Inventaire faunistique", 3, "Suivi des écosystèmes"),
          ("Inventaire floristique", 3, "Suivi des écosystèmes"),
        ("Réduction des impacts humains", 2, "Conservation de la nature"),
          ("Perturbateurs endocriniens", 3, "Réduction des impacts humains"),
          ("Production alimentaire", 3, "Réduction des impacts humains"),
          ("Espèces invasives", 3, "Réduction des impacts humains"),
          ("Urbanisation", 3, "Réduction des impacts humains"),
          ("Energies fossiles", 3, "Réduction des impacts humains"),
          ("Energies renouvelables", 3, "Réduction des impacts humains"),
            ("Energie éolienne", 4, "Energies renouvelables"),
            ("Energie solaire", 4, "Energies renouvelables"),
          ("Diminution de la pollution", 3, "Réduction des impacts humains"),
            ("Pollution atmosphérique", 4, "Diminution de la pollution"),
            ("Pollution aquatique", 4, "Diminution de la pollution"),
            ("Pollution des sols", 4, "Diminution de la pollution"),
            ("Pollution sonore", 4, "Diminution de la pollution"),
            ("Pollution lumineuse", 4, "Diminution de la pollution"),
          ("Lutte contre le changement climatique", 3, "Réduction des impacts humains"),
            ("Réduction des émissions de gaz à effet de serre", 4, "Lutte contre le changement climatique"),
            ("Adaptation aux impacts du changement climatique", 4, "Lutte contre le changement climatique"),
          ("Erosion des sols", 3, "Réduction des impacts humains"),
          ("Gestion durable des ressources naturelles", 3, "Réduction des impacts humains"),
            ("Gestion durable de l'eau", 4, "Gestion durable des ressources naturelles"),
            ("Préservation de la biodiversité", 4, "Gestion durable des ressources naturelles"),
          ("Agriculture durable", 3, "Réduction des impacts humains"),
            ("Agroécologie", 4, "Agriculture durable"),
            ("Agriculture biologique", 4, "Agriculture durable"),
            ("Permaculture", 4, "Agriculture durable"),
            ("Agroforesterie", 4, "Agriculture durable"),
          ("Consommation responsable", 3, "Réduction des impacts humains"),
            ("Alimentation responsable", 4, "Consommation responsable"),
            ("Déplacement responsable", 4, "Consommation responsable"),
            ("Consommation de plastique responsable", 4, "Consommation responsable"),
            ("Consommation d'énergie", 4, "Consommation responsable"),
            ("Recyclage des déchets", 4, "Consommation responsable"),
      ("Evaluation des services écosystémiques", 1, "Applications interdisciplinaires"),
        ("Biomimétisme", 2, "Evaluation des services écosystémiques"),
        ("Auxiliaires de culture", 2, "Evaluation des services écosystémiques"),
]

# =============================================================================
# CLASSIFICATION OBJECTIF
# =============================================================================

OBJECTIFS = [
    ("Connexion à la nature", 0, None),
      ("Ressentir la nature", 1, "Connexion à la nature"),
      ("Observer la nature", 1, "Connexion à la nature"),
    ("Connaître la nature", 0, None),
      ("Découvrir la nature", 1, "Connaître la nature"),
      ("Comprendre la nature", 1, "Connaître la nature"),
    ("Agir pour la nature", 0, None),
      ("Aider la nature", 1, "Agir pour la nature"),
      ("Protéger la nature", 1, "Agir pour la nature"),
    ("Se mouvoir dans la nature", 0, None),
      ("Evoluer dans la nature", 1, "Se mouvoir dans la nature"),
      ("Se repérer dans la nature", 1, "Se mouvoir dans la nature"),
      ("Se cacher dans la nature", 1, "Se mouvoir dans la nature"),
      ("Se reposer dans la nature", 1, "Se mouvoir dans la nature"),
    ("Créer avec la nature", 0, None),
      ("Jouer dans la nature", 1, "Créer avec la nature"),
      ("Imaginer dans la nature", 1, "Créer avec la nature"),
      ("Construire dans la nature", 1, "Créer avec la nature"),
      ("Cuisiner dans la nature", 1, "Créer avec la nature"),
]

# =============================================================================
# MAIN
# =============================================================================

def import_hierarchie(conn, table, data):
    nom_to_id = {}
    inserted = 0

    for (nom, niveau, parent_nom) in data:
        parent_id = nom_to_id.get(parent_nom) if parent_nom else None

        try:
            cursor = conn.execute(f"""
                INSERT OR IGNORE INTO {table} (nom, parent_id, niveau)
                VALUES (?, ?, ?)
            """, (nom, parent_id, niveau))

            if cursor.rowcount > 0:
                nom_to_id[nom] = cursor.lastrowid
                inserted += 1
            else:
                row = conn.execute(
                    f"SELECT id FROM {table} WHERE nom=? AND (parent_id IS ? OR parent_id=?)",
                    (nom, parent_id, parent_id)
                ).fetchone()
                if row:
                    nom_to_id[nom] = row[0]

        except Exception as e:
            print(f"  ERREUR : Erreur '{nom}' : {e}")

    return inserted


def main():
    print("=" * 60)
    print("IMPORT CLASSIFICATION -> SQLITE")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERREUR : Base SQLite introuvable : {DB_PATH}")
        print("   Lancez d'abord create_schema.py")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    print("\n Import des thématiques...")
    n_them = import_hierarchie(conn, "thematique", THEMATIQUES)
    print(f"  OK {n_them} thématique(s) insérée(s)")

    print("\n Import des objectifs...")
    n_obj = import_hierarchie(conn, "objectif", OBJECTIFS)
    print(f"  OK {n_obj} objectif(s) inséré(s)")

    conn.commit()
    conn.close()

    print(f"\n{'=' * 60}")
    print("Import terminé.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
