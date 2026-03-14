# =============================================================================
# main.py
# =============================================================================
# Backend FastAPI pour la bibliothèque d'activités pédagogiques nature.
#
# Lancer avec : uvicorn main:app --reload
# Interface disponible sur : http://localhost:8000
# Doc API automatique : http://localhost:8000/docs
# =============================================================================

import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "activites.db"

app = FastAPI(title="Bibliothèque d'activités nature", version="1.0")

# Servir les fichiers statiques du frontend
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ============================================================================
# UTILITAIRES
# ============================================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def rows_to_list(rows):
    return [dict(r) for r in rows]

# ============================================================================
# PAGE PRINCIPALE
# ============================================================================

@app.get("/", response_class=HTMLResponse)
def index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return HTMLResponse("<h1>Frontend non trouvé — placez index.html dans /static</h1>")

# ============================================================================
# ACTIVITÉS
# ============================================================================

@app.get("/api/activites")
def liste_activites(
    q: Optional[str] = Query(None, description="Recherche texte"),
    lieu: Optional[str] = Query(None, description="Intérieur / Extérieur / Intérieur/Extérieur"),
    mois: Optional[str] = Query(None, description="jan, fev, mar, avr, mai, jun, jul, aou, sep, oct, nov, dec"),
    meteo: Optional[str] = Query(None, description="nuage, soleil, pluie, vent"),
    thematique_id: Optional[int] = Query(None),
    objectif_id: Optional[int] = Query(None),
    pedagogie_id: Optional[int] = Query(None),
    theorie_id: Optional[int] = Query(None),
    cycle_ids: Optional[str] = Query(None, description="IDs séparés par des virgules"),
    attendu_ids: Optional[str] = Query(None, description="IDs séparés par des virgules"),
    tag_ids: Optional[str] = Query(None, description="IDs de tags séparés par des virgules"),
    competence: Optional[str] = Query(None, description="individuel, binôme, petit groupe, grand groupe"),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    """Recherche et filtrage des activités."""
    conn = get_db()

    conditions = []
    params = []

    # Recherche texte
    if q:
        conditions.append("(a.nom LIKE ? OR a.description LIKE ? OR a.objectif_texte LIKE ?)")
        params += [f"%{q}%", f"%{q}%", f"%{q}%"]

    # Lieu
    if lieu:
        if lieu.lower() == "extérieur":
            conditions.append("(a.lieu = ? OR a.lieu = ?)")
            params.extend(["Extérieur", "Intérieur/Extérieur"])
        elif lieu.lower() == "intérieur":
            conditions.append("(a.lieu = ? OR a.lieu = ?)")
            params.extend(["Intérieur", "Intérieur/Extérieur"])
        else:
            conditions.append("a.lieu = ?")
            params.append(lieu)

    # Météo
    if meteo:
        col = f"meteo_{meteo}"
        conditions.append(f"a.{col} = 1")

    # Mois
    if mois:
        col = f"mois_{mois}"
        conditions.append(f"a.{col} = 1")

    # Format groupe
    if competence:
        conditions.append("a.format_groupe = ?")
        params.append(competence)

    # Thématique (inclut les sous-thématiques via récursion)
    if thematique_id:
        conditions.append("""
            a.id IN (
                SELECT at2.activite_id FROM activite_thematique at2
                WHERE at2.thematique_id IN (
                    WITH RECURSIVE sous_themes(id) AS (
                        SELECT id FROM thematique WHERE id = ?
                        UNION ALL
                        SELECT t.id FROM thematique t
                        INNER JOIN sous_themes st ON t.parent_id = st.id
                    )
                    SELECT id FROM sous_themes
                )
            )
        """)
        params.append(thematique_id)

    # Objectif
    if objectif_id:
        conditions.append("""
            a.id IN (
                SELECT ao.activite_id FROM activite_objectif ao
                WHERE ao.objectif_id IN (
                    WITH RECURSIVE sous_obj(id) AS (
                        SELECT id FROM objectif WHERE id = ?
                        UNION ALL
                        SELECT o.id FROM objectif o
                        INNER JOIN sous_obj so ON o.parent_id = so.id
                    )
                    SELECT id FROM sous_obj
                )
            )
        """)
        params.append(objectif_id)

    # Pédagogie
    if pedagogie_id:
        conditions.append("a.id IN (SELECT activite_id FROM activite_pedagogie WHERE pedagogie_id = ?)")
        params.append(pedagogie_id)

    # Théorie
    if theorie_id:
        conditions.append("a.id IN (SELECT activite_id FROM activite_theorie WHERE theorie_id = ?)")
        params.append(theorie_id)

    # Attendus scolaires (plusieurs possibles)
    if attendu_ids:
        ids = [int(x) for x in attendu_ids.split(',') if x.strip().isdigit()]
        if ids:
            placeholders = ','.join('?' * len(ids))
            conditions.append(f"a.id IN (SELECT activite_id FROM activite_attendu WHERE attendu_id IN ({placeholders}))")
            params += ids

    # Cycles (plusieurs possibles)
    # Tags
    if tag_ids:
        ids = [int(x) for x in tag_ids.split(',') if x.strip().isdigit()]
        if ids:
            placeholders = ','.join('?' * len(ids))
            conditions.append(f"a.id IN (SELECT activite_id FROM activite_tag WHERE tag_id IN ({placeholders}))")
            params += ids

    if cycle_ids and not attendu_ids:
        ids = [int(x) for x in cycle_ids.split(',') if x.strip().isdigit()]
        if ids:
            placeholders = ','.join('?' * len(ids))
            conditions.append(f"a.id IN (SELECT activite_id FROM activite_cycle WHERE cycle_id IN ({placeholders}))")
            params += ids

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    # Compter le total
    total = conn.execute(
        f"SELECT COUNT(*) FROM activite a {where_clause}", params
    ).fetchone()[0]

    # Récupérer les résultats
    rows = conn.execute(
        f"""
        SELECT a.id, a.nom, a.lieu, a.duree_min, a.format_groupe,
               a.meteo_nuage, a.meteo_soleil, a.meteo_pluie, a.meteo_vent,
               a.mois_jan, a.mois_fev, a.mois_mar, a.mois_avr,
               a.mois_mai, a.mois_jun, a.mois_jul, a.mois_aou,
               a.mois_sep, a.mois_oct, a.mois_nov, a.mois_dec,
               a.description, a.objectif_texte, a.materiel_produit,
               a.chemin_dossier, a.anime
        FROM activite a
        {where_clause}
        ORDER BY a.nom
        LIMIT ? OFFSET ?
        """,
        params + [limit, offset]
    ).fetchall()

    conn.close()
    return {"total": total, "offset": offset, "limit": limit, "results": rows_to_list(rows)}


@app.get("/api/activites/{activite_id}")
def detail_activite(activite_id: int):
    """Détail complet d'une activité avec toutes ses relations."""
    conn = get_db()

    activite = conn.execute("SELECT * FROM activite WHERE id = ?", (activite_id,)).fetchone()
    if not activite:
        raise HTTPException(status_code=404, detail="Activité introuvable")

    result = dict(activite)

    # Thématiques
    result["thematiques"] = rows_to_list(conn.execute("""
        SELECT t.id, t.nom, t.niveau FROM thematique t
        INNER JOIN activite_thematique at2 ON t.id = at2.thematique_id
        WHERE at2.activite_id = ?
    """, (activite_id,)).fetchall())

    # Objectifs
    result["objectifs"] = rows_to_list(conn.execute("""
        SELECT o.id, o.nom, o.niveau FROM objectif o
        INNER JOIN activite_objectif ao ON o.id = ao.objectif_id
        WHERE ao.activite_id = ?
    """, (activite_id,)).fetchall())

    # Pédagogies
    result["pedagogies"] = rows_to_list(conn.execute("""
        SELECT p.id, p.nom FROM pedagogie p
        INNER JOIN activite_pedagogie ap ON p.id = ap.pedagogie_id
        WHERE ap.activite_id = ?
    """, (activite_id,)).fetchall())

    # Théories
    result["theories"] = rows_to_list(conn.execute("""
        SELECT t.id, t.nom FROM theorie_apprentissage t
        INNER JOIN activite_theorie at2 ON t.id = at2.theorie_id
        WHERE at2.activite_id = ?
    """, (activite_id,)).fetchall())

    # Attendus scolaires
    result["attendus"] = rows_to_list(conn.execute("""
        SELECT ats.id, ats.libelle, ats.domaine, ats.sous_domaine, c.nom as cycle, c.code as cycle_code
        FROM attendu_scolaire ats
        INNER JOIN activite_attendu aa ON ats.id = aa.attendu_id
        INNER JOIN cycle c ON ats.cycle_id = c.id
        WHERE aa.activite_id = ?
    """, (activite_id,)).fetchall())

    # Tags
    result["tags"] = rows_to_list(conn.execute("""
        SELECT t.id, t.nom FROM tag t
        INNER JOIN activite_tag at2 ON t.id = at2.tag_id
        WHERE at2.activite_id = ?
        ORDER BY t.nom
    """, (activite_id,)).fetchall())

    # Compétences
    result["competences"] = rows_to_list(conn.execute("""
        SELECT c.id, c.nom, c.categorie FROM competence c
        INNER JOIN activite_competence ac ON c.id = ac.competence_id
        WHERE ac.activite_id = ?
    """, (activite_id,)).fetchall())

    # Tags
    result["tags"] = rows_to_list(conn.execute("""
        SELECT t.id, t.nom FROM tag t
        INNER JOIN activite_tag at2 ON t.id = at2.tag_id
        WHERE at2.activite_id = ?
    """, (activite_id,)).fetchall())

    # Relations avec d'autres activités
    result["relations"] = rows_to_list(conn.execute("""
        SELECT a.id, a.nom, r.type_relation FROM activite a
        INNER JOIN relation_activite r ON a.id = r.activite_cible_id
        WHERE r.activite_source_id = ?
        UNION
        SELECT a.id, a.nom, r.type_relation FROM activite a
        INNER JOIN relation_activite r ON a.id = r.activite_source_id
        WHERE r.activite_cible_id = ? AND r.type_relation = 'complementaire'
    """, (activite_id, activite_id)).fetchall())

    conn.close()
    return result



@app.put("/api/activites/{activite_id}")
def modifier_activite(activite_id: int, data: dict):
    """Met a jour les champs d'une activite."""
    conn = get_db()
    try:
        # Champs simples
        champs = ["nom", "description", "objectif_texte", "lieu", "duree_min", "format_groupe", "anime",
                  "meteo_soleil", "meteo_pluie", "meteo_vent", "meteo_nuage", "meteo_nuit",
                  "mois_jan","mois_fev","mois_mar","mois_avr","mois_mai","mois_jun",
                  "mois_jul","mois_aou","mois_sep","mois_oct","mois_nov","mois_dec"]
        updates = {k: data[k] for k in champs if k in data}
        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            conn.execute(
                f"UPDATE activite SET {set_clause} WHERE id = ?",
                list(updates.values()) + [activite_id]
            )

        # Tags
        if "tag_ids" in data:
            conn.execute("DELETE FROM activite_tag WHERE activite_id = ?", (activite_id,))
            for tid in data["tag_ids"]:
                conn.execute("INSERT OR IGNORE INTO activite_tag (activite_id, tag_id) VALUES (?,?)", (activite_id, tid))

        # Thematiques
        if "thematique_ids" in data:
            conn.execute("DELETE FROM activite_thematique WHERE activite_id = ?", (activite_id,))
            for tid in data["thematique_ids"]:
                conn.execute("INSERT OR IGNORE INTO activite_thematique (activite_id, thematique_id) VALUES (?,?)", (activite_id, tid))

        # Objectifs
        if "objectif_ids" in data:
            conn.execute("DELETE FROM activite_objectif WHERE activite_id = ?", (activite_id,))
            for oid in data["objectif_ids"]:
                conn.execute("INSERT OR IGNORE INTO activite_objectif (activite_id, objectif_id) VALUES (?,?)", (activite_id, oid))

        # Attendus + cycles derives
        if "attendu_ids" in data:
            conn.execute("DELETE FROM activite_attendu WHERE activite_id = ?", (activite_id,))
            conn.execute("DELETE FROM activite_cycle WHERE activite_id = ?", (activite_id,))
            for aid in data["attendu_ids"]:
                conn.execute("INSERT OR IGNORE INTO activite_attendu (activite_id, attendu_id) VALUES (?,?)", (activite_id, aid))
            if data["attendu_ids"]:
                placeholders = ",".join("?" * len(data["attendu_ids"]))
                cycle_ids = [r[0] for r in conn.execute(
                    f"SELECT DISTINCT cycle_id FROM attendu_scolaire WHERE id IN ({placeholders})",
                    data["attendu_ids"]
                ).fetchall()]
                for cid in cycle_ids:
                    conn.execute("INSERT OR IGNORE INTO activite_cycle (activite_id, cycle_id) VALUES (?,?)", (activite_id, cid))

        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/activites/{activite_id}/ouvrir-dossier")
def ouvrir_dossier(activite_id: int):
    """Ouvre le dossier de l'activité dans l'explorateur Windows."""
    conn = get_db()
    row = conn.execute("SELECT chemin_dossier FROM activite WHERE id = ?", (activite_id,)).fetchone()
    conn.close()

    if not row or not row["chemin_dossier"]:
        raise HTTPException(status_code=404, detail="Chemin introuvable")

    chemin = row["chemin_dossier"].replace("file:///", "").replace("/", "\\")
    path = Path(chemin)

    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Dossier introuvable : {chemin}")

    subprocess.Popen(f'explorer "{path}"')
    return {"status": "ok", "chemin": chemin}

# ============================================================================
# RÉFÉRENTIELS
# ============================================================================

@app.get("/api/thematiques")
def liste_thematiques(parent_id: Optional[int] = Query(None, description="None = racines")):
    """Retourne les thématiques d'un niveau (racines si parent_id absent)."""
    conn = get_db()
    if parent_id is None:
        rows = conn.execute(
            "SELECT id, nom, niveau FROM thematique WHERE parent_id IS NULL ORDER BY nom"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, nom, niveau FROM thematique WHERE parent_id = ? ORDER BY nom",
            (parent_id,)
        ).fetchall()
    conn.close()
    return rows_to_list(rows)


@app.get("/api/objectifs")
def liste_objectifs(parent_id: Optional[int] = Query(None)):
    conn = get_db()
    if parent_id is None:
        rows = conn.execute(
            "SELECT id, nom, niveau FROM objectif WHERE parent_id IS NULL ORDER BY nom"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, nom, niveau FROM objectif WHERE parent_id = ? ORDER BY nom",
            (parent_id,)
        ).fetchall()
    conn.close()
    return rows_to_list(rows)


@app.get("/api/thematiques/arbre")
def arbre_thematiques():
    """Retourne l'arbre complet des thematiques."""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, nom, niveau, parent_id FROM thematique ORDER BY niveau, nom"
    ).fetchall()
    conn.close()
    return _construire_arbre(rows_to_list(rows))


@app.get("/api/objectifs/arbre")
def arbre_objectifs():
    """Retourne l'arbre complet des objectifs."""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, nom, niveau, parent_id FROM objectif ORDER BY niveau, nom"
    ).fetchall()
    conn.close()
    return _construire_arbre(rows_to_list(rows))


def _construire_arbre(nodes):
    """Transforme une liste plate en arbre imbriqué."""
    index = {n["id"]: {**n, "children": []} for n in nodes}
    roots = []
    for n in nodes:
        if n["parent_id"] is None:
            roots.append(index[n["id"]])
        elif n["parent_id"] in index:
            index[n["parent_id"]]["children"].append(index[n["id"]])
    return roots


@app.get("/api/pedagogies")
def liste_pedagogies():
    conn = get_db()
    rows = conn.execute("SELECT id, nom, resume FROM pedagogie ORDER BY nom").fetchall()
    conn.close()
    return rows_to_list(rows)


@app.get("/api/theories")
def liste_theories():
    conn = get_db()
    rows = conn.execute("SELECT id, nom, resume FROM theorie_apprentissage ORDER BY nom").fetchall()
    conn.close()
    return rows_to_list(rows)


@app.get("/api/cycles")
def liste_cycles():
    conn = get_db()
    rows = conn.execute("SELECT id, nom, code, ages FROM cycle ORDER BY id").fetchall()
    conn.close()
    return rows_to_list(rows)


@app.get("/api/cycles/{cycle_id}/attendus")
def attendus_par_cycle(cycle_id: int, domaine: Optional[str] = Query(None)):
    conn = get_db()
    if domaine:
        rows = conn.execute(
            "SELECT ats.id, ats.domaine, ats.sous_domaine, ats.libelle, c.code as cycle_code, c.id as cycle_id FROM attendu_scolaire ats JOIN cycle c ON c.id=ats.cycle_id WHERE ats.cycle_id = ? AND ats.domaine = ? ORDER BY ats.domaine, ats.libelle",
            (cycle_id, domaine)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT ats.id, ats.domaine, ats.sous_domaine, ats.libelle, c.code as cycle_code, c.id as cycle_id FROM attendu_scolaire ats JOIN cycle c ON c.id=ats.cycle_id WHERE ats.cycle_id = ? ORDER BY ats.domaine, ats.libelle",
            (cycle_id,)
        ).fetchall()
    conn.close()
    return rows_to_list(rows)


@app.get("/api/competences")
def liste_competences():
    conn = get_db()
    rows = conn.execute("SELECT id, nom, categorie FROM competence ORDER BY categorie, nom").fetchall()
    conn.close()
    return rows_to_list(rows)


@app.get("/api/tags")
def liste_tags(q: Optional[str] = Query(None)):
    conn = get_db()
    if q:
        rows = conn.execute(
            "SELECT id, nom FROM tag WHERE nom LIKE ? ORDER BY nom", (f"%{q}%",)
        ).fetchall()
    else:
        rows = conn.execute("SELECT id, nom FROM tag ORDER BY nom").fetchall()
    conn.close()
    return rows_to_list(rows)

# ============================================================================
# PLANIFICATION — SÉJOURS
# ============================================================================

class SejourCreate(BaseModel):
    nom: str
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    public: Optional[str] = None
    cycle_id: Optional[int] = None
    effectif: Optional[int] = None
    thematique_generale: Optional[str] = None
    notes: Optional[str] = None


@app.get("/api/tags")
def get_tags():
    conn = get_db()
    rows = conn.execute("SELECT id, nom FROM tag ORDER BY nom").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/api/tags")
def creer_tag(data: dict):
    nom = data.get("nom", "").strip()
    if not nom:
        raise HTTPException(status_code=400, detail="Nom requis")
    conn = get_db()
    try:
        cur = conn.execute("INSERT INTO tag (nom) VALUES (?)", (nom,))
        conn.commit()
        tag_id = cur.lastrowid
        conn.close()
        return {"id": tag_id, "nom": nom}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/tags/{tag_id}")
def modifier_tag(tag_id: int, data: dict):
    nom = data.get("nom", "").strip()
    if not nom:
        raise HTTPException(status_code=400, detail="Nom requis")
    conn = get_db()
    conn.execute("UPDATE tag SET nom = ? WHERE id = ?", (nom, tag_id))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.delete("/api/tags/{tag_id}")
def supprimer_tag(tag_id: int):
    conn = get_db()
    conn.execute("DELETE FROM activite_tag WHERE tag_id = ?", (tag_id,))
    conn.execute("DELETE FROM tag WHERE id = ?", (tag_id,))
    conn.commit()
    conn.close()
    return {"ok": True}

@app.get("/api/sejours")
def liste_sejours():
    conn = get_db()
    rows = conn.execute("SELECT * FROM sejour ORDER BY date_debut DESC").fetchall()
    conn.close()
    return rows_to_list(rows)


@app.post("/api/sejours")
def creer_sejour(sejour: SejourCreate):
    conn = get_db()
    cursor = conn.execute("""
        INSERT INTO sejour (nom, date_debut, date_fin, public, cycle_id, effectif, thematique_generale, notes)
        VALUES (:nom, :date_debut, :date_fin, :public, :cycle_id, :effectif, :thematique_generale, :notes)
    """, sejour.dict())
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, **sejour.dict()}


@app.get("/api/sejours/{sejour_id}")
def detail_sejour(sejour_id: int):
    conn = get_db()
    sejour = conn.execute("SELECT * FROM sejour WHERE id = ?", (sejour_id,)).fetchone()
    if not sejour:
        raise HTTPException(status_code=404, detail="Séjour introuvable")

    result = dict(sejour)

    # Séquences avec leurs activités
    sequences = conn.execute(
        "SELECT * FROM sequence WHERE sejour_id = ? ORDER BY ordre, date, moment",
        (sejour_id,)
    ).fetchall()

    result["sequences"] = []
    for seq in sequences:
        seq_dict = dict(seq)
        seq_dict["activites"] = rows_to_list(conn.execute("""
            SELECT a.id, a.nom, a.duree_min, a.lieu, sa.ordre, sa.duree_prevue, sa.notes
            FROM activite a
            INNER JOIN sequence_activite sa ON a.id = sa.activite_id
            WHERE sa.sequence_id = ?
            ORDER BY sa.ordre
        """, (seq["id"],)).fetchall())
        result["sequences"].append(seq_dict)

    conn.close()
    return result


# ============================================================================
# STATISTIQUES
# ============================================================================

@app.get("/api/stats")
def statistiques():
    conn = get_db()
    stats = {
        "total_activites": conn.execute("SELECT COUNT(*) FROM activite").fetchone()[0],
        "activites_avec_description": conn.execute("SELECT COUNT(*) FROM activite WHERE description IS NOT NULL").fetchone()[0],
        "activites_animees": conn.execute("SELECT COUNT(*) FROM activite WHERE anime = 1").fetchone()[0],
        "total_thematiques": conn.execute("SELECT COUNT(*) FROM thematique").fetchone()[0],
        "total_pedagogies": conn.execute("SELECT COUNT(*) FROM pedagogie").fetchone()[0],
        "total_theories": conn.execute("SELECT COUNT(*) FROM theorie_apprentissage").fetchone()[0],
        "total_tags": conn.execute("SELECT COUNT(*) FROM tag").fetchone()[0],
        "total_sejours": conn.execute("SELECT COUNT(*) FROM sejour").fetchone()[0],
        "activites_par_lieu": rows_to_list(conn.execute(
            "SELECT lieu, COUNT(*) as nb FROM activite GROUP BY lieu ORDER BY nb DESC"
        ).fetchall()),
    }
    conn.close()
    return stats
