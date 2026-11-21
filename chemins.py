# chemins.py — chemins qui dépendent de l'ordinateur sur lequel l'outil tourne.
#
# Rien n'est écrit en dur : tout est déduit de l'emplacement de ce fichier,
# qui se trouve toujours dans  <Dropbox>\Outils\BDD activités\_OUTIL
# quel que soit le PC (nom d'utilisateur, nom du dossier Dropbox…).

import re
import socket
from pathlib import Path
from typing import Optional

POSTE = socket.gethostname()                      # nom de l'ordinateur (pour info / logs)
OUTIL_DIR = Path(__file__).resolve().parent       # ...\_OUTIL
DROPBOX = OUTIL_DIR.parents[2]                    # ...\Dropbox

ACTIVITES_DIR = DROPBOX / "Animation" / "Activités v2"
DOSSIER_ANNEE = DROPBOX / "CPAC" / "Documents projets" / "2026-2027"

# Préfixe d'un chemin Dropbox enregistré sur n'importe quel poste :
# « C:\Users\<qui>\Dropbox\ » ou « D:\Dropbox (Perso)\ », etc.
_PREFIXE_DROPBOX = re.compile(r"^.*?\\Dropbox(?: \([^)\\]*\))?\\", re.IGNORECASE)


def localiser(chemin: Optional[str]) -> Optional[str]:
    """Convertit un chemin enregistré (éventuellement sur un autre PC, éventuellement
    en « file:///… ») en chemin Windows valable sur ce PC.

    La base est partagée par Dropbox entre les ordinateurs : on ne la modifie pas,
    on traduit les chemins au moment de les lire.
    """
    if not chemin:
        return chemin
    s = str(chemin)
    if s.startswith("file:///"):
        s = s[8:]
    s = s.replace("/", "\\")
    m = _PREFIXE_DROPBOX.match(s)
    if m:
        s = str(DROPBOX) + "\\" + s[m.end():]
    return s
