# =============================================================================
# taches.py
# =============================================================================
# Avancement du travail : tâches classées par catégorie (Séjours, Pôle biodiversité,
# Équipe médiateurs, Autres…), avec un état (à faire / en cours / fait),
# une priorité et une échéance facultative.
# Les rappels de séjours en retard viennent du suivi des séjours (sejours.py).
# =============================================================================

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "activites.db"

# (clé, nom affiché) — la clé ne change jamais, le nom peut être renommé
CATEGORIES_INITIALES = [
    ("sejours", "Séjours"),
    ("biodiversite", "Pôle biodiversité"),
    ("equipe", "Équipe médiateurs"),
    ("autres", "Autres"),
]
PROTEGEES = {"sejours", "autres"}          # catégories qu'on ne peut pas supprimer
STATUTS = ("a_faire", "en_cours", "fait")
PRIORITES = (1, 2, 3)                      # 1 = haute, 2 = normale, 3 = basse

router = APIRouter(prefix="/api/taches", tags=["tâches"])


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_schema():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tache_categorie (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            cle    TEXT UNIQUE,
            nom    TEXT NOT NULL,
            ordre  INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS tache (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            categorie_id  INTEGER NOT NULL REFERENCES tache_categorie(id),
            titre         TEXT NOT NULL,
            note          TEXT,
            statut        TEXT NOT NULL DEFAULT 'a_faire',
            priorite      INTEGER NOT NULL DEFAULT 2,
            echeance      TEXT,
            cree_le       TEXT NOT NULL,
            fait_le       TEXT
        );
    """)
    if conn.execute("SELECT COUNT(*) FROM tache_categorie").fetchone()[0] == 0:
        conn.executemany("INSERT INTO tache_categorie (cle, nom, ordre) VALUES (?, ?, ?)",
                         [(cle, nom, i) for i, (cle, nom) in enumerate(CATEGORIES_INITIALES)])
    # Ordre de priorité numéroté (1 = à faire en premier), ajouté après coup
    if "rang" not in {r["name"] for r in conn.execute("PRAGMA table_info(tache)")}:
        conn.execute("ALTER TABLE tache ADD COLUMN rang INTEGER")
        for (cat,) in conn.execute("SELECT id FROM tache_categorie").fetchall():
            _renumeroter(conn, cat)
    conn.commit()
    conn.close()


def _renumeroter(conn, categorie_id: int, tache_id: Optional[int] = None, position: Optional[int] = None):
    """Renumérote 1, 2, 3… les tâches non faites d'une catégorie.
    Si `tache_id` et `position` sont donnés, place cette tâche à cette position."""
    ids = [r["id"] for r in conn.execute(
        "SELECT id FROM tache WHERE categorie_id=? AND statut!='fait' "
        "ORDER BY rang IS NULL, rang, priorite, echeance IS NULL, echeance, id", (categorie_id,))]
    if tache_id in ids and position is not None:
        ids.remove(tache_id)
        ids.insert(max(0, min(position - 1, len(ids))), tache_id)
    conn.executemany("UPDATE tache SET rang=? WHERE id=?", [(i + 1, t) for i, t in enumerate(ids)])
    conn.execute("UPDATE tache SET rang=NULL WHERE categorie_id=? AND statut='fait'", (categorie_id,))


# ----------------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------------

def _verifier(champs: dict) -> dict:
    if "titre" in champs:
        champs["titre"] = (champs["titre"] or "").strip()
        if not champs["titre"]:
            raise HTTPException(400, "Le titre est obligatoire.")
    if "note" in champs:
        champs["note"] = (champs["note"] or "").strip() or None
    if "statut" in champs and champs["statut"] not in STATUTS:
        raise HTTPException(400, f"État inconnu : {champs['statut']}")
    if "priorite" in champs and champs["priorite"] not in PRIORITES:
        raise HTTPException(400, "Priorité : 1 (haute), 2 (normale) ou 3 (basse).")
    if champs.get("rang") is not None and champs["rang"] < 1:
        raise HTTPException(400, "Le numéro de priorité doit être 1 ou plus.")
    if champs.get("echeance"):
        try:
            date.fromisoformat(champs["echeance"])
        except ValueError:
            raise HTTPException(400, "Échéance invalide (format AAAA-MM-JJ).")
    elif "echeance" in champs:
        champs["echeance"] = None
    return champs


def _categorie_existe(conn, categorie_id: int):
    if not conn.execute("SELECT 1 FROM tache_categorie WHERE id=?", (categorie_id,)).fetchone():
        raise HTTPException(404, "Catégorie introuvable.")


# ----------------------------------------------------------------------------
# Tâches
# ----------------------------------------------------------------------------

@router.get("")
def lister():
    ensure_schema()
    conn = get_db()
    cats = [dict(r) for r in conn.execute("SELECT id, cle, nom, ordre FROM tache_categorie ORDER BY ordre, id")]
    for c in cats:
        c["protegee"] = c["cle"] in PROTEGEES
    taches = [dict(r) for r in conn.execute("SELECT * FROM tache ORDER BY categorie_id, rang IS NULL, rang, id")]
    conn.close()
    return {"categories": cats, "taches": taches}


class TacheIn(BaseModel):
    titre: str
    categorie_id: int
    rang: Optional[int] = None            # position voulue ; vide = à la fin de la liste
    echeance: Optional[str] = None
    note: Optional[str] = None


class TacheMaj(BaseModel):
    titre: Optional[str] = None
    categorie_id: Optional[int] = None
    statut: Optional[str] = None
    rang: Optional[int] = None
    echeance: Optional[str] = None
    note: Optional[str] = None


def _toutes(conn) -> list:
    """Toutes les tâches : après un changement d'ordre, plusieurs tâches changent de numéro."""
    return [dict(r) for r in conn.execute("SELECT * FROM tache ORDER BY categorie_id, rang IS NULL, rang, id")]


@router.post("")
def creer(t: TacheIn):
    ensure_schema()
    champs = _verifier(t.model_dump())
    conn = get_db()
    _categorie_existe(conn, champs["categorie_id"])
    cur = conn.execute(
        "INSERT INTO tache (categorie_id, titre, note, echeance, cree_le, rang) VALUES (?, ?, ?, ?, ?, ?)",
        (champs["categorie_id"], champs["titre"], champs["note"], champs["echeance"],
         datetime.now().isoformat(timespec="seconds"), 10 ** 9))
    _renumeroter(conn, champs["categorie_id"], cur.lastrowid, champs["rang"])
    conn.commit()
    res = _toutes(conn)
    conn.close()
    return res


@router.patch("/{tache_id}")
def modifier(tache_id: int, t: TacheMaj):
    ensure_schema()
    champs = _verifier(t.model_dump(exclude_unset=True))
    position = champs.pop("rang", None)
    conn = get_db()
    avant = conn.execute("SELECT categorie_id, statut FROM tache WHERE id=?", (tache_id,)).fetchone()
    if not avant:
        conn.close()
        raise HTTPException(404, "Tâche introuvable.")
    if "categorie_id" in champs:
        _categorie_existe(conn, champs["categorie_id"])
    if "statut" in champs:
        champs["fait_le"] = date.today().isoformat() if champs["statut"] == "fait" else None
    change_cat = champs.get("categorie_id", avant["categorie_id"]) != avant["categorie_id"]
    rouverte = avant["statut"] == "fait" and champs.get("statut", "fait") != "fait"
    if change_cat or rouverte:
        champs["rang"] = 10 ** 9           # à la fin de sa (nouvelle) liste, sauf position demandée
    if champs:
        sets = ", ".join(f"{k}=?" for k in champs)
        conn.execute(f"UPDATE tache SET {sets} WHERE id=?", (*champs.values(), tache_id))
    _renumeroter(conn, avant["categorie_id"])
    _renumeroter(conn, champs.get("categorie_id", avant["categorie_id"]), tache_id, position)
    conn.commit()
    res = _toutes(conn)
    conn.close()
    return res


@router.delete("/{tache_id}")
def supprimer(tache_id: int):
    ensure_schema()
    conn = get_db()
    row = conn.execute("SELECT categorie_id FROM tache WHERE id=?", (tache_id,)).fetchone()
    conn.execute("DELETE FROM tache WHERE id=?", (tache_id,))
    if row:
        _renumeroter(conn, row["categorie_id"])
    conn.commit()
    res = _toutes(conn)
    conn.close()
    return res


# ----------------------------------------------------------------------------
# Catégories
# ----------------------------------------------------------------------------

class CategorieIn(BaseModel):
    nom: str


def _nom_categorie(c: CategorieIn) -> str:
    nom = c.nom.strip()
    if not nom:
        raise HTTPException(400, "Le nom est obligatoire.")
    return nom


@router.post("/categories")
def creer_categorie(c: CategorieIn):
    ensure_schema()
    nom = _nom_categorie(c)
    conn = get_db()
    ordre = conn.execute("SELECT COALESCE(MAX(ordre), 0) + 1 FROM tache_categorie").fetchone()[0]
    # « Autres » reste toujours en dernier
    conn.execute("UPDATE tache_categorie SET ordre=? WHERE cle='autres'", (ordre + 1,))
    cur = conn.execute("INSERT INTO tache_categorie (nom, ordre) VALUES (?, ?)", (nom, ordre))
    conn.commit()
    conn.close()
    return {"id": cur.lastrowid, "nom": nom}


@router.patch("/categories/{categorie_id}")
def renommer_categorie(categorie_id: int, c: CategorieIn):
    ensure_schema()
    nom = _nom_categorie(c)
    conn = get_db()
    _categorie_existe(conn, categorie_id)
    conn.execute("UPDATE tache_categorie SET nom=? WHERE id=?", (nom, categorie_id))
    conn.commit()
    conn.close()
    return {"ok": True}


@router.delete("/categories/{categorie_id}")
def supprimer_categorie(categorie_id: int):
    """Supprime la catégorie ; ses tâches sont déplacées dans « Autres »."""
    ensure_schema()
    conn = get_db()
    row = conn.execute("SELECT cle FROM tache_categorie WHERE id=?", (categorie_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Catégorie introuvable.")
    if row["cle"] in PROTEGEES:
        conn.close()
        raise HTTPException(400, "Cette catégorie ne peut pas être supprimée.")
    autres = conn.execute("SELECT id FROM tache_categorie WHERE cle='autres'").fetchone()["id"]
    # rang NULL → ces tâches passent après celles déjà présentes dans « Autres »
    conn.execute("UPDATE tache SET categorie_id=?, rang=NULL WHERE categorie_id=?", (autres, categorie_id))
    conn.execute("DELETE FROM tache_categorie WHERE id=?", (categorie_id,))
    _renumeroter(conn, autres)
    conn.commit()
    conn.close()
    return {"ok": True}
