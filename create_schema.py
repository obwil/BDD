# =============================================================================
# create_schema.py
# =============================================================================
# Crée la base SQLite avec toutes les tables nécessaires.
# Idempotent : peut être relancé sans détruire les données existantes.
# =============================================================================

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"

SCHEMA = """
-- ============================================================
-- RÉFÉRENTIELS (tables de base, indépendantes)
-- ============================================================

-- Thématiques hiérarchiques (auto-référentiel)
CREATE TABLE IF NOT EXISTS thematique (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL,
    parent_id   INTEGER REFERENCES thematique(id) ON DELETE SET NULL,
    niveau      INTEGER NOT NULL DEFAULT 0,  -- 0=racine, 1, 2, 3...
    UNIQUE(nom, parent_id)
);

-- Objectifs hiérarchiques (auto-référentiel)
CREATE TABLE IF NOT EXISTS objectif (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL,
    parent_id   INTEGER REFERENCES objectif(id) ON DELETE SET NULL,
    niveau      INTEGER NOT NULL DEFAULT 0,
    UNIQUE(nom, parent_id)
);

-- Pédagogies
CREATE TABLE IF NOT EXISTS pedagogie (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL UNIQUE,
    resume      TEXT,           -- résumé court pour l'API Claude
    notion_url  TEXT            -- lien vers la page Notion correspondante
);

-- Théories d'apprentissage
CREATE TABLE IF NOT EXISTS theorie_apprentissage (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL UNIQUE,
    resume      TEXT,
    notion_url  TEXT
);

-- Cycles scolaires
CREATE TABLE IF NOT EXISTS cycle (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL UNIQUE,   -- ex: "Cycle 1", "Cycle 2"
    code        TEXT NOT NULL UNIQUE,   -- ex: "C1", "C2", "C3", "C4"
    ages        TEXT                    -- ex: "3-6 ans"
);

-- Attendus scolaires (liés à un cycle)
CREATE TABLE IF NOT EXISTS attendu_scolaire (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_id    INTEGER NOT NULL REFERENCES cycle(id) ON DELETE CASCADE,
    domaine     TEXT,           -- ex: "Explorer le monde du vivant"
    sous_domaine TEXT,
    libelle     TEXT NOT NULL,  -- l'attendu exact du programme
    UNIQUE(cycle_id, libelle)
);

-- Compétences transversales
CREATE TABLE IF NOT EXISTS competence (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL UNIQUE,   -- ex: "Travail d'équipe", "Autonomie"
    categorie   TEXT                    -- ex: "sociale", "cognitive", "motrice"
);

-- Tags libres
CREATE TABLE IF NOT EXISTS tag (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL UNIQUE
);

-- ============================================================
-- ACTIVITÉ (table principale)
-- ============================================================

CREATE TABLE IF NOT EXISTS activite (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT NOT NULL UNIQUE,
    chemin_dossier  TEXT,               -- chemin absolu du dossier Dropbox
    anime           INTEGER DEFAULT 0,  -- 0/1 : déjà animée
    lieu            TEXT,               -- "Intérieur", "Extérieur", "Intérieur/Extérieur"
    duree_min       INTEGER,            -- durée en minutes
    effectif_min    INTEGER,
    effectif_max    INTEGER,

    -- Météo (0/1)
    meteo_nuage     INTEGER DEFAULT 0,
    meteo_nuit      INTEGER DEFAULT 0,
    meteo_soleil    INTEGER DEFAULT 0,
    meteo_pluie     INTEGER DEFAULT 0,
    meteo_vent      INTEGER DEFAULT 0,

    -- Mois (0/1)
    mois_jan        INTEGER DEFAULT 0,
    mois_fev        INTEGER DEFAULT 0,
    mois_mar        INTEGER DEFAULT 0,
    mois_avr        INTEGER DEFAULT 0,
    mois_mai        INTEGER DEFAULT 0,
    mois_jun        INTEGER DEFAULT 0,
    mois_jul        INTEGER DEFAULT 0,
    mois_aou        INTEGER DEFAULT 0,
    mois_sep        INTEGER DEFAULT 0,
    mois_oct        INTEGER DEFAULT 0,
    mois_nov        INTEGER DEFAULT 0,
    mois_dec        INTEGER DEFAULT 0,

    -- Champs remplis par l'API Claude
    description     TEXT,
    objectif_texte  TEXT,
    format_groupe   TEXT,   -- "individuel", "binôme", "petit groupe", "grand groupe"
    materiel_produit TEXT,  -- ce que l'enfant repart avec

    -- Métadonnées
    date_creation   TEXT DEFAULT (date('now')),
    date_maj        TEXT DEFAULT (date('now'))
);

-- ============================================================
-- RELATIONS MANY-TO-MANY
-- ============================================================

CREATE TABLE IF NOT EXISTS activite_thematique (
    activite_id     INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    thematique_id   INTEGER NOT NULL REFERENCES thematique(id) ON DELETE CASCADE,
    PRIMARY KEY (activite_id, thematique_id)
);

CREATE TABLE IF NOT EXISTS activite_objectif (
    activite_id     INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    objectif_id     INTEGER NOT NULL REFERENCES objectif(id) ON DELETE CASCADE,
    PRIMARY KEY (activite_id, objectif_id)
);

CREATE TABLE IF NOT EXISTS activite_pedagogie (
    activite_id     INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    pedagogie_id    INTEGER NOT NULL REFERENCES pedagogie(id) ON DELETE CASCADE,
    PRIMARY KEY (activite_id, pedagogie_id)
);

CREATE TABLE IF NOT EXISTS activite_theorie (
    activite_id     INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    theorie_id      INTEGER NOT NULL REFERENCES theorie_apprentissage(id) ON DELETE CASCADE,
    PRIMARY KEY (activite_id, theorie_id)
);

CREATE TABLE IF NOT EXISTS activite_attendu (
    activite_id     INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    attendu_id      INTEGER NOT NULL REFERENCES attendu_scolaire(id) ON DELETE CASCADE,
    PRIMARY KEY (activite_id, attendu_id)
);

CREATE TABLE IF NOT EXISTS activite_competence (
    activite_id     INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    competence_id   INTEGER NOT NULL REFERENCES competence(id) ON DELETE CASCADE,
    PRIMARY KEY (activite_id, competence_id)
);

CREATE TABLE IF NOT EXISTS activite_tag (
    activite_id     INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    tag_id          INTEGER NOT NULL REFERENCES tag(id) ON DELETE CASCADE,
    PRIMARY KEY (activite_id, tag_id)
);

-- ============================================================
-- RELATIONS ENTRE ACTIVITÉS
-- ============================================================

CREATE TABLE IF NOT EXISTS relation_activite (
    activite_source_id  INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    activite_cible_id   INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    type_relation       TEXT NOT NULL,  -- "complementaire", "prerequis", "prolongement"
    PRIMARY KEY (activite_source_id, activite_cible_id, type_relation)
);

-- ============================================================
-- PLANIFICATION
-- ============================================================

-- Séjour (ex: classe verte, sortie journée, séjour 5 jours)
CREATE TABLE IF NOT EXISTS sejour (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT NOT NULL,
    date_debut      TEXT,
    date_fin        TEXT,
    public          TEXT,           -- ex: "CE2", "6ème"
    cycle_id        INTEGER REFERENCES cycle(id),
    effectif        INTEGER,
    thematique_generale TEXT,
    notes           TEXT
);

-- Séquence (bloc dans un séjour : matin, après-midi, soirée...)
CREATE TABLE IF NOT EXISTS sequence (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sejour_id       INTEGER NOT NULL REFERENCES sejour(id) ON DELETE CASCADE,
    nom             TEXT NOT NULL,  -- ex: "Mardi matin", "Soirée 1"
    date            TEXT,
    moment          TEXT,           -- "matin", "après-midi", "soirée", "nuit"
    ordre           INTEGER DEFAULT 0,
    notes           TEXT
);

-- Activités dans une séquence (ordonnées)
CREATE TABLE IF NOT EXISTS sequence_activite (
    sequence_id     INTEGER NOT NULL REFERENCES sequence(id) ON DELETE CASCADE,
    activite_id     INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    ordre           INTEGER DEFAULT 0,
    duree_prevue    INTEGER,        -- durée prévue en minutes (peut différer de la durée standard)
    notes           TEXT,
    PRIMARY KEY (sequence_id, activite_id)
);

-- ============================================================
-- INDEX pour les recherches fréquentes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_activite_lieu     ON activite(lieu);
CREATE INDEX IF NOT EXISTS idx_activite_duree    ON activite(duree_min);
CREATE INDEX IF NOT EXISTS idx_thematique_parent ON thematique(parent_id);
CREATE INDEX IF NOT EXISTS idx_objectif_parent   ON objectif(parent_id);
CREATE INDEX IF NOT EXISTS idx_attendu_cycle     ON attendu_scolaire(cycle_id);
CREATE INDEX IF NOT EXISTS idx_sequence_sejour   ON sequence(sejour_id);
"""

def create_schema():
    print(f"Création de la base : {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()

    # Vérification
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print(f"\nOK {len(tables)} tables créées :")
    for (t,) in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  - {t} ({count} lignes)")

    conn.close()
    print("\nSchéma créé avec succès.")

if __name__ == "__main__":
    create_schema()
