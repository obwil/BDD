# =============================================================================
# generer_desc_depuis_video.py
# =============================================================================
# Pour chaque activité vide en BDD dont le dossier contient un _DESC_ vidéo :
#   - Uploade la vidéo via la Files API de Gemini
#   - Demande à Gemini de proposer une description d'activité pédagogique
#   - Écrit un fichier _DESC_<nom>.txt dans le dossier
#
# MODE SIMULATION (SIMULATION = True) :
#   - Aucune vidéo uploadée, aucun fichier écrit
#   - Affiche la liste des activités qui seraient traitées
#
# Prérequis :
#   pip install google-generativeai --break-system-packages
#
# Lancer avec : python generer_desc_depuis_video.py
# =============================================================================

import os
import sqlite3
import time
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

SIMULATION = False  # Mettre False pour vraiment uploader et écrire les fichiers

DROPBOX_ACTIVITES = Path(r"C:\Users\moina\Dropbox\Animation\Activités v2")
DB_PATH = Path(__file__).parent / "activites.db"

GEMINI_MODEL = "gemini-2.5-flash"
DELAI_ENTRE_APPELS = 20  # secondes entre chaque appel API

EXT_VIDEO = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"}

SYSTEM_PROMPT = """Tu es un assistant spécialisé en éducation à la nature et en pédagogie outdoor (école dehors).
Tu analyses des vidéos pour en extraire une description d'activité pédagogique utilisable par un animateur nature.
Tu rédiges en français, de manière claire et concise.
Tu ne définis jamais de tranche d'âge ni de public cible.
"""

PROMPT_ANALYSE = """Voici une vidéo en lien avec l'activité pédagogique nature intitulée : "{nom}"

Analyse cette vidéo et propose une description d'activité pédagogique structurée comprenant :
- Une description synthétique de l'activité (2-4 phrases)
- Le déroulement étape par étape
- Le matériel nécessaire
- Le lieu conseillé (intérieur / extérieur / les deux)
- La durée estimée
- D'éventuels prolongements ou variantes

Ne définis pas de tranche d'âge ni de public cible.
Rédige en français.
"""

# =============================================================================
# FONCTIONS
# =============================================================================

def get_activites_video():
    """Retourne la liste des activités vides dont le dossier contient un _DESC_ vidéo."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    vides = conn.execute("""
        SELECT a.id, a.nom FROM activite a
        WHERE (a.description IS NULL OR a.description = '')
        AND NOT EXISTS (SELECT 1 FROM activite_thematique at2 WHERE at2.activite_id = a.id)
        AND NOT EXISTS (SELECT 1 FROM activite_cycle ac WHERE ac.activite_id = a.id)
        ORDER BY a.nom
    """).fetchall()
    conn.close()

    resultats = []
    for r in vides:
        dossier = DROPBOX_ACTIVITES / r["nom"]
        if not dossier.exists():
            continue
        desc_files = [f for f in dossier.iterdir() if "_DESC_" in f.name.upper()]
        videos = [f for f in desc_files if f.suffix.lower() in EXT_VIDEO]
        if videos:
            resultats.append({
                "id": r["id"],
                "nom": r["nom"],
                "dossier": dossier,
                "videos": videos,
            })
    return resultats


def uploader_video(genai, video_path):
    """Upload une vidéo via Files API et attend qu'elle soit prête."""
    print(f"    Upload : {video_path.name} ({video_path.stat().st_size // 1024} Ko)...")
    video_file = genai.upload_file(path=str(video_path))

    # Attendre que le fichier soit traité
    max_attente = 120  # secondes
    debut = time.time()
    while video_file.state.name == "PROCESSING":
        if time.time() - debut > max_attente:
            raise TimeoutError(f"Fichier toujours en traitement après {max_attente}s")
        time.sleep(5)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name != "ACTIVE":
        raise RuntimeError(f"Fichier en état inattendu : {video_file.state.name}")

    print(f"    Fichier prêt : {video_file.uri}")
    return video_file


def appeler_gemini(model, video_file, nom_activite):
    """Envoie la vidéo à Gemini et retourne la description générée."""
    prompt = PROMPT_ANALYSE.format(nom=nom_activite)
    response = model.generate_content([video_file, prompt])
    return response.text.strip()


def desc_txt_path(dossier, nom_activite):
    """Retourne le chemin du fichier _DESC_.txt à créer."""
    nom_fichier = f"_DESC_{nom_activite}.txt"
    # Nettoyer les caractères invalides pour un nom de fichier Windows
    for c in r'\/:*?"<>|':
        nom_fichier = nom_fichier.replace(c, "_")
    return dossier / nom_fichier


# =============================================================================
# MAIN
# =============================================================================

def main():
    import google.generativeai as genai

    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY_ROM78")
    if not gemini_key:
        print("ERREUR : variable d'environnement GEMINI_API_KEY non définie.")
        return

    genai.configure(api_key=gemini_key)

    activites = get_activites_video()

    print("=" * 70)
    print(f"MODE : {'SIMULATION' if SIMULATION else 'RÉEL'}")
    print(f"Activités avec _DESC_ vidéo trouvées : {len(activites)}")
    print("=" * 70)

    for i, act in enumerate(activites, 1):
        print(f"\n[{i}/{len(activites)}] {act['nom']} (id={act['id']})")
        for v in act["videos"]:
            print(f"  Vidéo : {v.name} ({v.stat().st_size // 1024} Ko)")
        desc_path = desc_txt_path(act["dossier"], act["nom"])
        print(f"  → Fichier à créer : {desc_path.name}")

        if desc_path.exists():
            print(f"  ⚠️  _DESC_.txt existe déjà — sera ignoré en mode réel")

        if SIMULATION:
            continue

        # Mode réel
        if desc_path.exists():
            print(f"  Déjà traité, on passe.")
            continue

        try:
            model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=SYSTEM_PROMPT
            )
            # Utiliser la première vidéo trouvée
            video_file = uploader_video(genai, act["videos"][0])
            description = appeler_gemini(model, video_file, act["nom"])

            desc_path.write_text(description, encoding="utf-8")
            print(f"  ✅ _DESC_.txt écrit ({len(description)} caractères)")

            # Supprimer le fichier uploadé de Google
            genai.delete_file(video_file.name)
            print(f"  🗑️  Fichier supprimé de Google Files API")

            time.sleep(DELAI_ENTRE_APPELS)

        except Exception as e:
            print(f"  ❌ Erreur : {e}")
            continue

    print("\n" + "=" * 70)
    if SIMULATION:
        print(f"SIMULATION terminée. {len(activites)} activités seraient traitées.")
        print("Mettre SIMULATION = False pour lancer le traitement réel.")
    else:
        print("Traitement terminé.")
    print("=" * 70)

    import os as _os
    _os.system("pause")


if __name__ == "__main__":
    main()
