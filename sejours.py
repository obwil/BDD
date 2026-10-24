# =============================================================================
# sejours.py
# =============================================================================
# Planification des séjours : lien avec le classeur Excel des plannings,
# association d'activités aux après-midi / veillées (lundi→jeudi) et
# génération d'un document Word récapitulatif par séjour.
#
# Branché dans main.py via : app.include_router(sejours.router)
# =============================================================================

import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import doc2 as D2
import doc3 as D
import doc4 as D4
import mails as MAILS
import suivi as SU

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "activites.db"
CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_EXCEL = r"C:\Users\moina\Dropbox\CPAC\Documents projets\2026-2027\Plannings séjours_2026-2027.xlsx"

JOURS = ["lundi", "mardi", "mercredi", "jeudi"]
MOMENTS = ["après-midi", "veillée"]

router = APIRouter(prefix="/api/planning", tags=["planning séjours"])


# ----------------------------------------------------------------------------
# Base de données
# ----------------------------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Colonnes ajoutées à la table `sejour` existante (reprise de l'Excel)
SEJOUR_COLS = {
    "date_code": "TEXT",      # ex "28090210" tel que saisi dans l'Excel
    "niveau1": "TEXT",        # col A
    "niveau2": "TEXT",        # col B
    "categorie": "TEXT",      # col C (Hors EP / REP / REP+)
    "ecole": "TEXT",          # col D
    "enseignant": "TEXT",     # col E
    "classe_ar": "TEXT",      # col H
    "unite": "TEXT",          # col I
    "thematique_excel": "TEXT",  # col J
    "matin_texte": "TEXT",    # cellule du haut de la col K (activités du matin)
    "excel_row": "INTEGER",
    # Doc 3 « Projets enseignants Trimestre N »
    "trimestre": "INTEGER",
    "doc3_key": "TEXT",           # « date_debut|code unité » : identifie le séjour d'une semaine
    "mediateur_matin": "TEXT",
    "delai": "TEXT",              # date limite du dossier (colonne Délais)
    "objectifs_texte": "TEXT",    # objectifs pédagogiques du Doc 3
    "dossier_path": "TEXT",       # dossier du séjour dans Dropbox
}


def ensure_schema():
    conn = get_db()
    existing = {r["name"] for r in conn.execute("PRAGMA table_info(sejour)")}
    for col, typ in SEJOUR_COLS.items():
        if col not in existing:
            conn.execute(f"ALTER TABLE sejour ADD COLUMN {col} {typ}")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sequence_activite_attendu (
            sequence_id INTEGER NOT NULL,
            activite_id INTEGER NOT NULL,
            attendu_id  INTEGER NOT NULL REFERENCES attendu_scolaire(id) ON DELETE CASCADE,
            PRIMARY KEY (sequence_id, activite_id, attendu_id),
            FOREIGN KEY (sequence_id, activite_id)
                REFERENCES sequence_activite(sequence_id, activite_id) ON DELETE CASCADE
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS doc2_ecrit (
            sejour_id INTEGER NOT NULL REFERENCES sejour(id) ON DELETE CASCADE,
            cle       TEXT NOT NULL,
            texte     TEXT,
            PRIMARY KEY (sejour_id, cle)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sejour_suivi (
            sejour_id INTEGER NOT NULL REFERENCES sejour(id) ON DELETE CASCADE,
            etape     TEXT NOT NULL,
            fait      INTEGER NOT NULL DEFAULT 0,
            date      TEXT,
            PRIMARY KEY (sejour_id, etape)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sejour_ressource (
            sejour_id   INTEGER NOT NULL REFERENCES sejour(id) ON DELETE CASCADE,
            activite_id INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
            ordre       INTEGER DEFAULT 0,
            PRIMARY KEY (sejour_id, activite_id)
        )
    """)
    conn.commit()
    conn.close()


def _label(s: dict) -> str:
    d1, d2 = s["date_debut"], s["date_fin"]
    plage = f"{d1[8:10]}/{d1[5:7]} → {d2[8:10]}/{d2[5:7]}"
    qui = s.get("enseignant") or s.get("ecole") or "?"
    niv = "/".join(x for x in (s.get("niveau1"), s.get("niveau2")) if x)
    return f"{plage} · {qui}" + (f" ({niv})" if niv else "")


# ----------------------------------------------------------------------------
# Synchronisation Doc 3 → BDD
# ----------------------------------------------------------------------------

def _sejour_depuis_ligne(l: dict, referentiel: dict, roulement: dict) -> dict:
    s = {
        "date_debut": l["date_debut"], "date_fin": l["date_fin"],
        "niveau1": l["classes"], "niveau2": None, "public": l["classes"],
        "categorie": referentiel.get(D.norm(l["ecole"])),
        "ecole": l["ecole"], "enseignant": l["enseignants"], "unite": l["unite"],
        "thematique_excel": l["projet"], "thematique_generale": l["projet"],
        "objectifs_texte": l["objectifs"], "mediateur_matin": l["mediateur_matin"],
        "delai": l["delai"], "trimestre": l["trimestre"],
        "doc3_key": f"{l['date_debut']}|{l['unite_code']}",
        "matin_texte": D.texte_matin(l["unite"], l["date_debut"], roulement, l["date_fin"]),
        "excel_row": l["ligne"],
    }
    s["nom"] = _label(s)
    return s


COLS_MAJ = ["nom", "date_debut", "date_fin", "public", "niveau1", "niveau2", "categorie", "ecole",
            "enseignant", "unite", "thematique_excel", "thematique_generale", "objectifs_texte",
            "mediateur_matin", "delai", "trimestre", "doc3_key", "matin_texte", "excel_row"]


def _chercher_sejour(conn, s: dict):
    """Séjour déjà en base : même clé Doc 3, sinon un ancien séjour (import de l'ancien Excel)
    de même date de début dont l'enseignant correspond : il garde ses activités."""
    row = conn.execute("SELECT id FROM sejour WHERE doc3_key=?", (s["doc3_key"],)).fetchone()
    if row:
        return row["id"]
    noms = D.noms_famille(s["enseignant"])
    for r in conn.execute("SELECT id, enseignant FROM sejour WHERE doc3_key IS NULL AND date_debut=?",
                          (s["date_debut"],)):
        if any(n in D.norm(r["enseignant"]) for n in noms):
            return r["id"]
    return None


def _synchroniser(conn, trimestres=(1, 2, 3)) -> dict:
    """Lit les « Projets enseignants Trimestre N » et enregistre les séjours où tu es médiateur d'après-midi."""
    referentiel, roulement = D.lire_referentiel(), D.lire_roulement()
    if not conn.execute("SELECT 1 FROM sejour WHERE doc3_key IS NOT NULL").fetchone():
        import shutil  # première synchronisation : on garde une copie de la base
        shutil.copy2(DB_PATH, DB_PATH.with_name(DB_PATH.name + ".bak-avant-doc3"))
    ajoutes = maj = 0
    trimestres_lus, avertissements = [], []
    if not roulement:
        avertissements.append("Roulement des matinées introuvable : les matinées ne seront pas renseignées.")
    for n in trimestres:
        doc = D.lire_doc3(n)
        avertissements += doc["avertissements"]
        if doc["fichier"] is None:
            trimestres_lus.append({"trimestre": n, "fichier": None, "sejours": 0})
            continue
        mes = D.mes_sejours(doc["lignes"], "am")
        trimestres_lus.append({"trimestre": n, "fichier": str(doc["fichier"]), "sejours": len(mes)})
        for l in mes:
            s = _sejour_depuis_ligne(l, referentiel, roulement)
            if not s["categorie"]:
                avertissements.append(f"École « {s['ecole']} » absente du référentiel des écoles.")
            if s["delai"] and s["delai"] > s["date_debut"]:
                avertissements.append(f"Délai du dossier ({s['delai']}) postérieur au séjour du {s['date_debut']} "
                                      f"({s['ecole']}, {s['enseignant']}) : à vérifier dans les Projets enseignants.")
            sid = _chercher_sejour(conn, s)
            if sid:
                conn.execute("UPDATE sejour SET " + ", ".join(f"{c}=:{c}" for c in COLS_MAJ) + " WHERE id=:id",
                             {**s, "id": sid})
                maj += 1
            else:
                sid = conn.execute("INSERT INTO sejour (" + ", ".join(COLS_MAJ) + ") VALUES ("
                                   + ", ".join(f":{c}" for c in COLS_MAJ) + ")", s).lastrowid
                ajoutes += 1
            d = D.trouver_dossier(s)
            conn.execute("UPDATE sejour SET dossier_path=? WHERE id=?", (str(d) if d else None, sid))
    orphelins = conn.execute("""
        SELECT s.nom FROM sejour s WHERE s.doc3_key IS NULL AND s.date_code IS NOT NULL AND EXISTS
          (SELECT 1 FROM sequence q JOIN sequence_activite sa ON sa.sequence_id=q.id WHERE q.sejour_id=s.id)
    """).fetchall()
    for o in orphelins:
        avertissements.append(f"Ancien séjour non retrouvé dans les Projets enseignants, avec des activités placées : {o['nom']}")
    conn.commit()
    manquants = _dossiers_manquants(conn)
    return {"ajoutes": ajoutes, "mis_a_jour": maj, "trimestres": trimestres_lus,
            "avertissements": sorted(set(avertissements)), "dossiers_manquants": len(manquants)}


@router.post("/sync")
def synchroniser():
    ensure_schema()
    conn = get_db()
    res = _synchroniser(conn)
    conn.close()
    return res


# ----------------------------------------------------------------------------
# Lecture
# ----------------------------------------------------------------------------

@router.get("/sejours")
def liste_sejours():
    ensure_schema()
    conn = get_db()
    rows = conn.execute("""
        SELECT s.id, s.nom, s.date_debut, s.date_fin, s.enseignant, s.ecole, s.public, s.trimestre,
          s.categorie, s.delai, s.dossier_path,
          (SELECT COUNT(*) FROM sequence q JOIN sequence_activite sa ON sa.sequence_id=q.id
            WHERE q.sejour_id=s.id) AS nb_activites
        FROM sejour s WHERE s.doc3_key IS NOT NULL
        ORDER BY s.date_debut, s.excel_row""").fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["dossier_existe"] = bool(d["dossier_path"] and Path(d["dossier_path"]).is_dir())
        out.append(d)
    return out


# ----------------------------------------------------------------------------
# Dossiers de séjour (copie du modèle B)
# ----------------------------------------------------------------------------

def _dossiers_manquants(conn, trimestre: Optional[int] = None) -> list:
    out = []
    for r in conn.execute("SELECT * FROM sejour WHERE doc3_key IS NOT NULL ORDER BY date_debut"):
        s = dict(r)
        if trimestre is not None and s["trimestre"] != trimestre:
            continue
        if not (s["dossier_path"] and Path(s["dossier_path"]).is_dir()):
            out.append(s)
    return out


@router.get("/dossiers/manquants")
def dossiers_manquants():
    """Aperçu : dossiers qui seraient créés (rien n'est écrit)."""
    ensure_schema()
    conn = get_db()
    res = []
    for s in _dossiers_manquants(conn):
        r = D.creer_dossier(s, dry_run=True)
        res.append({"id": s["id"], "nom": s["nom"], **r})
    conn.close()
    return res


def _creer_dossiers(conn, trimestre: Optional[int] = None) -> list:
    """Crée les dossiers manquants depuis le modèle B ; « déroulé et objectifs » est pré-rempli aussitôt."""
    res = []
    for s in _dossiers_manquants(conn, trimestre):
        r = D.creer_dossier(s)
        if r["ok"]:
            conn.execute("UPDATE sejour SET dossier_path=? WHERE id=?", (r["dossier"], s["id"]))
            conn.commit()
            r["doc2"] = _maj_doc2(conn, s["id"])
        res.append({"id": s["id"], "nom": s["nom"], "trimestre": s["trimestre"], **r})
    conn.commit()
    return res


def _remplir_edt(n: int) -> dict:
    """Pré-remplit « EDT trimestre N » avec les semaines où tu es médiateur du matin."""
    return {"trimestre": n, **D4.remplir_edt(n, D.lire_doc3(n)["lignes"])}


@router.post("/dossiers/creer")
def dossiers_creer():
    """Crée les dossiers manquants (tous trimestres) puis met à jour l'EDT des trimestres concernés."""
    ensure_schema()
    conn = get_db()
    res = _creer_dossiers(conn)
    conn.close()
    trimestres = sorted({r["trimestre"] for r in res if r["ok"] and r["trimestre"]})
    return {"dossiers": res, "edt": [_remplir_edt(n) for n in trimestres]}


# ----------------------------------------------------------------------------
# Démarrer un trimestre : tout d'un coup
# ----------------------------------------------------------------------------

@router.get("/trimestres/{n}/apercu")
def apercu_trimestre(n: int):
    """Ce que « Démarrer le trimestre » ferait. Rien n'est écrit."""
    doc = D.lire_doc3(n)
    if doc["fichier"] is None:
        raise HTTPException(404, f"Aucun « Projets enseignants Trimestre {n} » trouvé "
                                 f"(dossier « Trimestre {n} » ou dossier de l'année).")
    referentiel, roulement = D.lire_referentiel(), D.lire_roulement()
    sejours = []
    for l in D.mes_sejours(doc["lignes"], "am"):
        s = _sejour_depuis_ligne(l, referentiel, roulement)
        existant = D.trouver_dossier(s)
        sejours.append({"nom": s["nom"], "dossier_existe": bool(existant),
                        "dossier": str(existant or D.dossier_trimestre(n) / D.nom_dossier(s))})
    return {"trimestre": n, "fichier": str(doc["fichier"]), "sejours": sejours,
            "a_creer": sum(1 for x in sejours if not x["dossier_existe"]),
            "edt": D4.remplir_edt(n, doc["lignes"], dry_run=True),
            "avertissements": doc["avertissements"]}


@router.post("/trimestres/{n}/demarrer")
def demarrer_trimestre(n: int):
    """Enchaîne : lecture du Doc 3, création des dossiers (avec « déroulé et objectifs » pré-rempli),
    puis pré-remplissage de l'EDT du trimestre (Doc 4)."""
    ensure_schema()
    if D.lire_doc3(n)["fichier"] is None:
        raise HTTPException(404, f"Aucun « Projets enseignants Trimestre {n} » trouvé.")
    conn = get_db()
    sync = _synchroniser(conn, (n,))
    conn.commit()
    dossiers = _creer_dossiers(conn, n)
    conn.close()
    return {"trimestre": n, "sync": sync, "dossiers": dossiers, "edt": _remplir_edt(n)}


def _maj_doc2(conn, sejour_id: int, strict: bool = False) -> dict:
    """Écrit les infos du séjour et les activités choisies dans « déroulé et objectifs ».
    strict=True : lève une erreur HTTP (bouton) ; sinon renvoie un statut, sans jamais bloquer l'appelant."""
    def echec(code, message):
        if strict:
            raise HTTPException(code, message)
        return {"ok": False, "message": message}

    s = _charger_sejour(conn, sejour_id)
    dossier = Path(s["dossier_path"]) if s.get("dossier_path") and Path(s["dossier_path"]).is_dir() else D.trouver_dossier(s)
    if not dossier:
        return echec(409, "Pas de dossier pour ce séjour : crée-le d'abord.")
    try:
        fichier = D2.assurer_doc2(dossier, s)
        ecrits = {r["cle"]: r["texte"] for r in conn.execute(
            "SELECT cle, texte FROM doc2_ecrit WHERE sejour_id=?", (sejour_id,))}
        res = D2.remplir_doc2(fichier, s, s["planning"], ecrits)
    except PermissionError:
        return echec(423, "« Déroulé et objectifs » est ouvert dans Word : ferme-le puis réessaie.")
    except FileNotFoundError as e:
        return echec(404, str(e))
    conn.execute("DELETE FROM doc2_ecrit WHERE sejour_id=?", (sejour_id,))
    conn.executemany("INSERT INTO doc2_ecrit (sejour_id, cle, texte) VALUES (?,?,?)",
                     [(sejour_id, k, v) for k, v in res["ecrits"].items()])
    conn.commit()
    return {"ok": True, "fichier": res["fichier"], "remplis": res["remplis"], "conserves": res["conserves"]}


@router.post("/sejours/{sejour_id}/doc2")
def mettre_a_jour_doc2(sejour_id: int):
    """Met à jour « déroulé et objectifs » du dossier (le copie depuis le modèle B s'il manque).
    Les cases que tu as retouchées sont conservées."""
    ensure_schema()
    conn = get_db()
    if not conn.execute("SELECT 1 FROM sejour WHERE id=?", (sejour_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Séjour introuvable")
    res = _maj_doc2(conn, sejour_id, strict=True)
    conn.close()
    return res


def _charger_sejour(conn, sejour_id: int) -> dict:
    s = conn.execute("SELECT * FROM sejour WHERE id=?", (sejour_id,)).fetchone()
    if not s:
        raise HTTPException(404, "Séjour introuvable")
    res = dict(s)
    planning = {j: {m: [] for m in MOMENTS} for j in JOURS}
    seqs = conn.execute("SELECT * FROM sequence WHERE sejour_id=?", (sejour_id,)).fetchall()
    for q in seqs:
        if q["date"] not in planning or q["moment"] not in MOMENTS:
            continue
        acts = conn.execute("""
            SELECT a.id, a.nom, a.description, a.objectif_texte, sa.ordre
            FROM sequence_activite sa JOIN activite a ON a.id=sa.activite_id
            WHERE sa.sequence_id=? ORDER BY sa.ordre""", (q["id"],)).fetchall()
        for a in acts:
            d = dict(a)
            planning[q["date"]][q["moment"]].append(d)
    res["planning"] = planning
    res["ressources"] = [dict(r) for r in conn.execute("""
        SELECT a.id, a.nom, a.description, a.duree_min, a.effectif_min, a.effectif_max,
               a.lieu, a.format_groupe, sr.ordre
        FROM sejour_ressource sr JOIN activite a ON a.id = sr.activite_id
        WHERE sr.sejour_id = ? ORDER BY sr.ordre""", (sejour_id,))]
    return res


@router.get("/sejours/{sejour_id}")
def detail_sejour(sejour_id: int):
    ensure_schema()
    conn = get_db()
    res = _charger_sejour(conn, sejour_id)
    conn.close()
    return res


# ----------------------------------------------------------------------------
# Association activité ↔ créneau
# ----------------------------------------------------------------------------

class SlotIn(BaseModel):
    jour: str
    moment: str
    activite_id: int


def _check_slot(jour: str, moment: str):
    if jour not in JOURS or moment not in MOMENTS:
        raise HTTPException(400, "Jour ou créneau invalide")


@router.put("/sejours/{sejour_id}/slot")
def ajouter_ou_maj_slot(sejour_id: int, slot: SlotIn):
    """Ajoute l'activité au créneau (sans effet si elle y est déjà)."""
    _check_slot(slot.jour, slot.moment)
    ensure_schema()
    conn = get_db()
    if not conn.execute("SELECT 1 FROM sejour WHERE id=?", (sejour_id,)).fetchone():
        raise HTTPException(404, "Séjour introuvable")
    if not conn.execute("SELECT 1 FROM activite WHERE id=?", (slot.activite_id,)).fetchone():
        raise HTTPException(404, "Activité introuvable")

    seq = conn.execute("SELECT id FROM sequence WHERE sejour_id=? AND date=? AND moment=?",
                       (sejour_id, slot.jour, slot.moment)).fetchone()
    if seq:
        seq_id = seq["id"]
    else:
        ordre = JOURS.index(slot.jour) * 2 + MOMENTS.index(slot.moment)
        seq_id = conn.execute(
            "INSERT INTO sequence (sejour_id, nom, date, moment, ordre) VALUES (?,?,?,?,?)",
            (sejour_id, f"{slot.jour.capitalize()} {slot.moment}", slot.jour, slot.moment, ordre)
        ).lastrowid

    if not conn.execute("SELECT 1 FROM sequence_activite WHERE sequence_id=? AND activite_id=?",
                        (seq_id, slot.activite_id)).fetchone():
        nxt = conn.execute("SELECT COALESCE(MAX(ordre),-1)+1 FROM sequence_activite WHERE sequence_id=?",
                           (seq_id,)).fetchone()[0]
        conn.execute("INSERT INTO sequence_activite (sequence_id, activite_id, ordre) VALUES (?,?,?)",
                     (seq_id, slot.activite_id, nxt))

    conn.commit()
    res = _charger_sejour(conn, sejour_id)
    res["doc2"] = _maj_doc2(conn, sejour_id)
    conn.close()
    return res


@router.delete("/sejours/{sejour_id}/slot")
def retirer_slot(sejour_id: int, jour: str, moment: str, activite_id: int):
    _check_slot(jour, moment)
    ensure_schema()
    conn = get_db()
    seq = conn.execute("SELECT id FROM sequence WHERE sejour_id=? AND date=? AND moment=?",
                       (sejour_id, jour, moment)).fetchone()
    if seq:
        conn.execute("DELETE FROM sequence_activite WHERE sequence_id=? AND activite_id=?",
                     (seq["id"], activite_id))
        conn.commit()
    res = _charger_sejour(conn, sejour_id)
    res["doc2"] = _maj_doc2(conn, sejour_id)
    conn.close()
    return res


# ----------------------------------------------------------------------------
# Ressources en autonomie (jeux, supports… tirés de la base)
# ----------------------------------------------------------------------------

class RessourceIn(BaseModel):
    activite_id: int


@router.put("/sejours/{sejour_id}/ressource")
def ajouter_ressource(sejour_id: int, r: RessourceIn):
    ensure_schema()
    conn = get_db()
    if not conn.execute("SELECT 1 FROM sejour WHERE id=?", (sejour_id,)).fetchone():
        raise HTTPException(404, "Séjour introuvable")
    if not conn.execute("SELECT 1 FROM activite WHERE id=?", (r.activite_id,)).fetchone():
        raise HTTPException(404, "Activité introuvable")
    nxt = conn.execute("SELECT COALESCE(MAX(ordre),-1)+1 FROM sejour_ressource WHERE sejour_id=?",
                       (sejour_id,)).fetchone()[0]
    conn.execute("INSERT OR IGNORE INTO sejour_ressource (sejour_id, activite_id, ordre) VALUES (?,?,?)",
                 (sejour_id, r.activite_id, nxt))
    conn.commit()
    res = _charger_sejour(conn, sejour_id)
    res["doc2"] = _maj_doc2(conn, sejour_id)
    conn.close()
    return res


@router.delete("/sejours/{sejour_id}/ressource/{activite_id}")
def retirer_ressource(sejour_id: int, activite_id: int):
    ensure_schema()
    conn = get_db()
    conn.execute("DELETE FROM sejour_ressource WHERE sejour_id=? AND activite_id=?",
                 (sejour_id, activite_id))
    conn.commit()
    res = _charger_sejour(conn, sejour_id)
    res["doc2"] = _maj_doc2(conn, sejour_id)
    conn.close()
    return res


# ----------------------------------------------------------------------------
# Suivi des séjours et mails
# ----------------------------------------------------------------------------

def _dossier_existant(s: dict) -> Optional[Path]:
    if s.get("dossier_path") and Path(s["dossier_path"]).is_dir():
        return Path(s["dossier_path"])
    return D.trouver_dossier(s)


def _suivi_sejour(conn, sejour_id: int, manuels: Optional[dict] = None) -> dict:
    """Étapes détectées (dossier, appel, emploi du temps, document) + étapes cochées à la main."""
    s = _charger_sejour(conn, sejour_id)
    if manuels is None:
        manuels = {r["etape"]: bool(r["fait"]) for r in conn.execute(
            "SELECT etape, fait FROM sejour_suivi WHERE sejour_id=?", (sejour_id,))}
    dossier = _dossier_existant(s)
    pl = s["planning"]
    apres = sum(1 for j in JOURS if pl[j]["après-midi"])
    veillees = sum(1 for j in JOURS if pl[j]["veillée"])
    notes = SU.notes_appel(dossier) if dossier else None
    auto = {
        "dossier": (bool(dossier), None),
        "appel": (bool(notes and notes[0] > 0), f"{notes[0]}/{notes[1]} réponses" if notes else None),
        "planning": (apres == len(JOURS), f"après-midis {apres}/4 · veillées {veillees}/4"),
    }
    etapes = []
    for cle, libelle, est_auto in SU.ETAPES:
        fait, detail = auto[cle] if est_auto else (manuels.get(cle, False), None)
        etapes.append({"cle": cle, "label": libelle, "auto": est_auto, "fait": fait, "detail": detail})
    valide = manuels.get("valide", False)
    suivante = next((e["label"] for e in etapes if not e["fait"]), None)
    return {
        "id": s["id"], "nom": s["nom"], "trimestre": s["trimestre"], "date_debut": s["date_debut"],
        "date_fin": s["date_fin"], "ecole": s["ecole"], "classes": s["niveau1"], "enseignant": s["enseignant"],
        "delai": s["delai"], "delai_statut": SU.statut_delai(s["delai"], valide, s["date_fin"]),
        "etapes": etapes, "faites": sum(1 for e in etapes if e["fait"]), "total": len(etapes),
        "prochaine": suivante,
    }


@router.get("/suivi")
def suivi_sejours():
    """Une ligne par séjour, une colonne par étape."""
    ensure_schema()
    conn = get_db()
    manuels: dict = {}
    for r in conn.execute("SELECT sejour_id, etape, fait FROM sejour_suivi"):
        manuels.setdefault(r["sejour_id"], {})[r["etape"]] = bool(r["fait"])
    ids = [r["id"] for r in conn.execute("SELECT id FROM sejour WHERE doc3_key IS NOT NULL ORDER BY date_debut")]
    res = [_suivi_sejour(conn, i, manuels.get(i, {})) for i in ids]
    conn.close()
    return res


@router.get("/sejours/{sejour_id}/suivi")
def suivi_un_sejour(sejour_id: int):
    ensure_schema()
    conn = get_db()
    res = _suivi_sejour(conn, sejour_id)
    conn.close()
    return res


class SuiviIn(BaseModel):
    etape: str
    fait: bool


@router.put("/sejours/{sejour_id}/suivi")
def cocher_etape(sejour_id: int, c: SuiviIn):
    """Coche ou décoche une étape manuelle (mail d'invitation envoyé, document envoyé, validé)."""
    if c.etape not in SU.MANUELLES:
        raise HTTPException(400, "Cette étape se coche automatiquement.")
    ensure_schema()
    conn = get_db()
    if not conn.execute("SELECT 1 FROM sejour WHERE id=?", (sejour_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Séjour introuvable")
    conn.execute("""INSERT INTO sejour_suivi (sejour_id, etape, fait, date) VALUES (?,?,?,date('now'))
                    ON CONFLICT(sejour_id, etape) DO UPDATE SET fait=excluded.fait, date=excluded.date""",
                 (sejour_id, c.etape, int(c.fait)))
    conn.commit()
    res = _suivi_sejour(conn, sejour_id)
    conn.close()
    return res


class MailIn(BaseModel):
    modele: str
    disponibilites: str = ""
    enregistrer: bool = True


@router.post("/sejours/{sejour_id}/mail")
def rediger_mail(sejour_id: int, m: MailIn):
    """Rédige un mail à partir des Projets enseignants et l'enregistre dans le dossier du séjour."""
    if m.modele not in MAILS.MODELES:
        raise HTTPException(400, "Modèle de mail inconnu.")
    ensure_schema()
    conn = get_db()
    s = _charger_sejour(conn, sejour_id)
    conn.close()
    dossier = _dossier_existant(s)
    notes = SU.notes_appel(dossier) if dossier else None
    objet, corps = MAILS.rediger(m.modele, s, m.disponibilites, appel_fait=bool(notes and notes[0] > 0))
    fichier = None
    if m.enregistrer and dossier:
        f = dossier / f"Mail - {MAILS.MODELES[m.modele]}.txt"
        try:
            f.write_text(f"Objet : {objet}\n\n{corps}\n", encoding="utf-8")
            fichier = str(f)
        except PermissionError:
            fichier = None
    return {"objet": objet, "corps": corps, "fichier": fichier,
            "a_preciser": MAILS.A_PRECISER in corps}
