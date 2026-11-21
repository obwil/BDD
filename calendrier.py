# =============================================================================
# calendrier.py
# =============================================================================
# Calendrier des journées et nuits dédiées à la nature (Nuit de la chouette,
# Fête de la science, Journée des zones humides…).
# L'interface les affiche près du filtre « Mois ».
#
# Les événements sont dans la table `evenement_calendrier` de activites.db.
# Le jeu initial n'est inséré que si la table est vide : les modifications faites
# ensuite dans la base ne sont jamais écrasées.
# =============================================================================

import sqlite3
from pathlib import Path

from fastapi import APIRouter

DB_PATH = Path(__file__).parent / "activites.db"

router = APIRouter(prefix="/api/calendrier", tags=["calendrier"])

# type : 'journee' (journée ou nuit dédiée). Les phénomènes de saison et l'astronomie
#        ne figurent pas ici : ils sont traités par des activités de la base.
# mois_debut / mois_fin : 1 à 12 (la période peut passer par la fin de l'année)
# jour_tri : jour du mois qui sert à classer (0 si aucun)
# verifie : 1 si la date a été confirmée par une source, 0 sinon
EVENEMENTS_INITIAUX = [
    # (nom, type, mois_debut, mois_fin, quand, jour_tri, verifie)
    ("Journée mondiale des zones humides", "journee", 2, 2, "2 février", 2, 1),
    ("Journée des forêts et Journée de l'eau", "journee", 3, 3, "21 et 22 mars", 21, 1),
    ("Nuit de la chouette", "journee", 3, 3, "mars des années impaires (prochaine : mars 2027)", 0, 1),
    ("Jour de la Terre", "journee", 4, 4, "22 avril", 22, 1),
    ("Journée mondiale des abeilles", "journee", 5, 5, "20 mai", 20, 1),
    ("Fête de la nature et Journée de la biodiversité", "journee", 5, 5, "vers le 22 mai", 22, 1),
    ("Nuit européenne des chauves-souris", "journee", 8, 8, "dernier week-end d'août (29-30 août en 2026)", 29, 1),
    ("Fête de la science", "journee", 10, 10, "début octobre (2-12 octobre en 2026)", 2, 1),
    ("Jour de la nuit", "journee", 10, 10, "2e samedi d'octobre (10 octobre en 2026)", 10, 1),
    # --- Autres journées thématiques ---
    ("Comptage national des oiseaux des jardins", "journee", 1, 1, "dernier week-end de janvier", 25, 1),
    ("Journée mondiale de la vie sauvage", "journee", 3, 3, "3 mars", 3, 1),
    ("Journée mondiale de la météorologie", "journee", 3, 3, "23 mars", 23, 1),
    ("Journée mondiale des oiseaux migrateurs", "journee", 5, 5, "2e samedi de mai", 11, 1),
    ("Comptage national des oiseaux des jardins", "journee", 5, 5, "dernier week-end de mai", 25, 1),
    ("Journée mondiale de l'environnement", "journee", 6, 6, "5 juin", 5, 1),
    ("Fête des mares", "journee", 6, 6, "première quinzaine de juin", 6, 1),
    ("Journée mondiale des océans", "journee", 6, 6, "8 juin", 8, 1),
    ("Nuits des étoiles", "journee", 8, 8, "début août (7-9 août en 2026)", 7, 1),
    ("Journée mondiale du nettoyage de la planète", "journee", 9, 9, "vers le 20 septembre (20 septembre en 2026)", 20, 1),
    ("Journée mondiale des oiseaux migrateurs", "journee", 10, 10, "2e samedi d'octobre", 11, 1),
    ("Journée mondiale des sols", "journee", 12, 12, "5 décembre", 5, 1),
    ("Journée internationale de la montagne", "journee", 12, 12, "11 décembre", 11, 1),
    ("Journée mondiale des glaciers", "journee", 3, 3, "21 mars", 21, 1),
    ("Semaine pour les alternatives aux pesticides", "journee", 3, 3, "20-30 mars (les 10 premiers jours du printemps)", 20, 1),
    ("Rendez-vous aux jardins", "journee", 6, 6, "début juin (5-7 juin en 2026)", 5, 1),
    ("Journée mondiale des animaux", "journee", 10, 10, "4 octobre", 4, 1),
    ("Semaine européenne de la réduction des déchets", "journee", 11, 11, "fin novembre (22-30 novembre en 2025)", 22, 1),
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS evenement_calendrier (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nom         TEXT NOT NULL,
            type        TEXT NOT NULL DEFAULT 'journee',
            mois_debut  INTEGER NOT NULL,
            mois_fin    INTEGER NOT NULL,
            quand       TEXT,
            jour_tri    INTEGER NOT NULL DEFAULT 0,
            verifie     INTEGER NOT NULL DEFAULT 0
        )
    """)
    if conn.execute("SELECT COUNT(*) FROM evenement_calendrier").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO evenement_calendrier (nom, type, mois_debut, mois_fin, quand, jour_tri, verifie)"
            " VALUES (?,?,?,?,?,?,?)",
            EVENEMENTS_INITIAUX,
        )
    conn.commit()
    conn.close()


ensure_table()


@router.get("")
def liste_evenements():
    """Tous les événements ; l'interface filtre selon le mois choisi."""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, nom, type, mois_debut, mois_fin, quand, jour_tri, verifie"
        " FROM evenement_calendrier ORDER BY jour_tri, nom"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
