# =============================================================================
# retours.py
# =============================================================================
# Retours d'expérience par activité : « ce qui a bien marché » / « à améliorer »,
# saisis depuis l'emploi du temps d'un séjour.
#
# Source de vérité : table SQLite `retour_activite`.
# Le fichier « retours.md » du dossier de l'activité est réécrit à chaque
# enregistrement (support de lecture : le modifier à la main n'a pas d'effet).
# =============================================================================

from datetime import date, timedelta
from pathlib import Path
from typing import Optional

FICHIER = "retours.md"
JOURS = ["lundi", "mardi", "mercredi", "jeudi"]
PLUIE = "pluie"  # valeur de `creneau` pour une activité jouée à la place d'une autre à cause de la pluie

SCHEMA = """
CREATE TABLE IF NOT EXISTS retour_activite (
    sejour_id   INTEGER NOT NULL REFERENCES sejour(id) ON DELETE CASCADE,
    activite_id INTEGER NOT NULL REFERENCES activite(id) ON DELETE CASCADE,
    creneau     TEXT NOT NULL,          -- « lundi|après-midi » ou « pluie »
    bien        TEXT,
    ameliorer   TEXT,
    maj         TEXT,
    PRIMARY KEY (sejour_id, activite_id, creneau)
)
"""


def dossier_activite(chemin: Optional[str]) -> Optional[Path]:
    if not chemin:
        return None
    p = Path(chemin.replace("file:///", "").replace("/", "\\"))
    return p if p.is_dir() else None


def date_du_creneau(date_debut: Optional[str], creneau: str) -> Optional[date]:
    """Date réelle du créneau (le séjour commence le lundi). None pour « pluie » ou si inconnue."""
    jour = creneau.split("|")[0]
    if jour not in JOURS or not date_debut:
        return None
    try:
        return date.fromisoformat(date_debut[:10]) + timedelta(days=JOURS.index(jour))
    except ValueError:
        return None


def libelle_creneau(creneau: str) -> str:
    return "si pluie" if creneau == PLUIE else creneau.replace("|", " ")


def _fr(d: Optional[date]) -> str:
    return d.strftime("%d/%m/%Y") if d else ""


def lister(conn, activite_id: int) -> list:
    """Retours d'une activité, du plus récent au plus ancien, avec le contexte du séjour."""
    rows = conn.execute("""
        SELECT r.sejour_id, r.creneau, r.bien, r.ameliorer, r.maj,
               s.nom, s.date_debut, s.date_fin, s.public, s.niveau1, s.effectif
        FROM retour_activite r JOIN sejour s ON s.id = r.sejour_id
        WHERE r.activite_id = ?""", (activite_id,)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        dt = date_du_creneau(d["date_debut"], d["creneau"])
        d["date"] = dt.isoformat() if dt else (d["date_debut"] or "")[:10]
        d["creneau_label"] = libelle_creneau(d["creneau"])
        d["public"] = d["public"] or d["niveau1"]
        out.append(d)
    out.sort(key=lambda x: (x["date"], x["maj"] or ""), reverse=True)
    return out


def _contexte(r: dict) -> str:
    morceaux = [r["public"], f"{r['effectif']} élèves" if r.get("effectif") else None]
    return " · ".join(m for m in morceaux if m)


def ecrire_fichier(conn, activite_id: int) -> dict:
    """Réécrit retours.md dans le dossier de l'activité. Ne lève jamais d'exception."""
    a = conn.execute("SELECT nom, chemin_dossier FROM activite WHERE id=?", (activite_id,)).fetchone()
    if not a:
        return {"ok": False, "message": "Activité introuvable."}
    dossier = dossier_activite(a["chemin_dossier"])
    if not dossier:
        return {"ok": False, "message": "Dossier de l'activité introuvable : retour enregistré dans la base seulement."}
    retours = lister(conn, activite_id)
    cible = dossier / FICHIER
    try:
        if not retours:
            if cible.exists():
                cible.unlink()
            return {"ok": True, "fichier": None}
        parts = [f"# Retours d'expérience — {a['nom']}\n"]
        for r in retours:
            d = date.fromisoformat(r["date"]) if r["date"] else None
            titre = " — ".join(x for x in (_fr(d), r["creneau_label"]) if x)
            parts.append(f"\n## {titre} · {r['nom']}\n")
            ctx = _contexte(r)
            if ctx:
                parts.append(f"*{ctx}*\n")
            if (r["bien"] or "").strip():
                parts.append(f"\n**Ce qui a bien marché**\n\n{r['bien'].strip()}\n")
            if (r["ameliorer"] or "").strip():
                parts.append(f"\n**À améliorer**\n\n{r['ameliorer'].strip()}\n")
        cible.write_text("".join(parts), encoding="utf-8")
        return {"ok": True, "fichier": str(cible)}
    except OSError as e:
        return {"ok": False, "message": f"{FICHIER} non écrit : {e}"}
