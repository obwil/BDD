# launcher_start.py — source de « BDD Launcher.exe » (compilé avec compiler_launcher.bat).
# Retrouve le dossier _OUTIL sur l'ordinateur où il est lancé, puis exécute lancer_launcher.bat.
# La fonction trouver_outil() sert aussi à « BDD Demarrage.exe » (demarrage_start.py).

import ctypes
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

RELATIF = Path("Outils") / "BDD activités" / "_OUTIL"


def dossiers_candidats():
    # 1) À côté de l'exe : il est normalement dans _OUTIL\dist\
    exe_dir = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
    yield exe_dir.parent
    yield exe_dir
    # 2) Emplacement du Dropbox déclaré par l'application Dropbox de ce poste
    for base in (os.environ.get("LOCALAPPDATA"), os.environ.get("APPDATA")):
        if not base:
            continue
        try:
            info = json.loads((Path(base) / "Dropbox" / "info.json").read_text(encoding="utf-8"))
        except Exception:
            continue
        for compte in info.values():
            if isinstance(compte, dict) and compte.get("path"):
                yield Path(compte["path"]) / RELATIF
    # 3) Emplacement par défaut
    yield Path.home() / "Dropbox" / RELATIF


def trouver_outil(fichier_repere: str) -> Optional[Path]:
    """Dossier _OUTIL de ce poste (celui qui contient `fichier_repere`)."""
    return next((d for d in dossiers_candidats() if (d / fichier_repere).exists()), None)


def alerte(message: str, titre: str):
    ctypes.windll.user32.MessageBoxW(0, message, titre, 0x10)


def message_introuvable() -> str:
    return ("Impossible de trouver le dossier « Dropbox\\Outils\\BDD activités\\_OUTIL » "
            f"sur cet ordinateur ({os.environ.get('COMPUTERNAME', '?')}).")


if __name__ == "__main__":
    dossier = trouver_outil("lancer_launcher.bat")
    if dossier:
        subprocess.Popen(["cmd", "/c", str(dossier / "lancer_launcher.bat")], cwd=str(dossier))
    else:
        alerte(message_introuvable(), "BDD Launcher")
