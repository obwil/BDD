# demarrage_start.py — source de « BDD Demarrage.exe » (compilé avec compiler_launcher.bat).
# Démarre l'application (serveur sur le port 8000) puis ouvre ses deux pages :
# la bibliothèque d'activités et l'avancement du travail.
# Fonctionne sur tous les postes : le dossier _OUTIL et Python sont retrouvés sur place.

import os
import subprocess
import time
import urllib.request

from launcher_start import alerte, message_introuvable, trouver_outil

TITRE = "BDD Démarrage"
BASE = "http://localhost:8000"
PAGES = [BASE + "/", BASE + "/static/taches.html"]
ATTENTE_MAX = 180   # secondes ; le premier lancement sur un poste installe les dépendances


def serveur_pret() -> bool:
    try:
        with urllib.request.urlopen(BASE + "/api/taches", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    if not serveur_pret():
        dossier = trouver_outil("serveur_app.bat")
        if not dossier:
            alerte(message_introuvable(), TITRE)
            return
        # Le serveur tourne dans sa propre fenêtre : la fermer arrête l'application
        serveur = subprocess.Popen(["cmd", "/c", str(dossier / "serveur_app.bat")], cwd=str(dossier),
                                   creationflags=subprocess.CREATE_NEW_CONSOLE)
        debut = time.time()
        while not serveur_pret():
            if serveur.poll() is not None or time.time() - debut > ATTENTE_MAX:
                alerte("L'application n'a pas démarré. Regardez la fenêtre « Serveur BDD » "
                       "pour voir le message d'erreur.", TITRE)
                return
            time.sleep(1)
    for url in PAGES:
        os.startfile(url)


if __name__ == "__main__":
    main()
