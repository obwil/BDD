# =============================================================================
# suivi.py
# =============================================================================
# Avancement d'un séjour : étapes détectées automatiquement (dossier, notes d'appel,
# emploi du temps, document généré) et étapes cochées à la main (mails, validation).
# Remplace la colonne « Avancement » de l'ancien Excel.
# =============================================================================

from datetime import date
from pathlib import Path
from typing import Optional, Tuple

# (clé, libellé, automatique ?)
ETAPES = [
    ("dossier", "Dossier créé", True),
    ("invitation", "Mail d'invitation envoyé", False),
    ("appel", "Appel fait", True),
    ("planning", "Emploi du temps rempli", True),
    ("document", "Document généré", True),
    ("envoye", "Document envoyé", False),
    ("valide", "Validé par l'enseignant", False),
]
MANUELLES = {cle for cle, _, auto in ETAPES if not auto}
JOURS_DELAI_PROCHE = 14


def notes_appel(dossier: Path) -> Optional[Tuple[int, int]]:
    """(réponses saisies, questions) dans « notes du 1er appel » ; None si le fichier n'existe pas."""
    f = next((x for x in sorted(dossier.glob("Points-premi*.docx")) if not x.name.startswith("~$")), None)
    if f is None:
        return None
    from docx import Document
    try:
        table = Document(f).tables[0]
    except Exception:
        return None
    lignes = table.rows[1:]  # la première ligne contient les en-têtes
    return sum(1 for r in lignes if r.cells[-1].text.strip()), len(lignes)


def document_genere(dossier: Path) -> bool:
    return any(not f.name.startswith("~$") for f in dossier.glob("Planning détaillé*.docx"))


def statut_delai(delai: Optional[str], valide: bool, date_fin: Optional[str] = None,
                 aujourdhui: Optional[date] = None) -> Optional[str]:
    """None (pas de délai), 'ok', 'proche' (dans les 14 jours) ou 'depasse'.
    Plus d'alerte une fois le séjour validé ou terminé."""
    if not delai:
        return None
    auj = aujourdhui or date.today()
    if valide or (date_fin and date.fromisoformat(date_fin) < auj):
        return "ok"
    d = date.fromisoformat(delai)
    if d < auj:
        return "depasse"
    return "proche" if (d - auj).days <= JOURS_DELAI_PROCHE else "ok"
