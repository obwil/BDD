# =============================================================================
# traduire_desc_anglais.py
# =============================================================================
# Pour chaque dossier d'activité :
#   - Cherche les fichiers _DESC_ en .txt, .docx, .pdf
#   - Détecte la langue (langdetect + pdfplumber pour PDFs natifs,
#     pytesseract pour PDFs scannés)
#   - Si anglais : envoie à Gemini pour traduction
#   - Enregistre le résultat en _DESC_FR_.docx dans le dossier
#
# Prérequis :
#   pip install langdetect pdfplumber python-docx pytesseract pillow --break-system-packages
#   Tesseract installé sur le système (tesseract --version pour vérifier)
#
# SIMULATION = True  -> rapport seul, aucun fichier créé, aucun appel Gemini
# SIMULATION = False -> traduction effective
# =============================================================================

import os
import sys
import time
import json
import base64
import sqlite3
from pathlib import Path
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

SIMULATION = False   # Mettre False pour traduire effectivement

DROPBOX_ACTIVITES = Path(r"C:\Users\moina\Dropbox\Animation\Activités v2")
DB_PATH           = Path(__file__).parent / "activites.db"
RAPPORT_PATH      = Path(__file__).parent / "rapport_traduction.txt"
GEMINI_MODEL      = "gemini-2.5-flash"
DELAI_ENTRE_APPELS = 10   # secondes entre appels Gemini
TESSERACT_CMD     = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Seuil : nombre minimum de mots pour que langdetect soit fiable
SEUIL_MOTS_DETECTION = 30

# Extensions ciblées uniquement
EXTENSIONS_CIBLES = {".txt", ".docx", ".pdf"}

# =============================================================================
# IMPORTS DYNAMIQUES
# =============================================================================

def verifier_dependances():
    manquantes = []
    try: import langdetect
    except ImportError: manquantes.append("langdetect")
    try: import pdfplumber
    except ImportError: manquantes.append("pdfplumber")
    try: import docx
    except ImportError: manquantes.append("python-docx")
    try: import pytesseract
    except ImportError: manquantes.append("pytesseract")
    try: import PIL
    except ImportError: manquantes.append("pillow")
    if manquantes:
        print(f"Dépendances manquantes : {', '.join(manquantes)}")
        print("Installer avec : pip install " + " ".join(manquantes) + " --break-system-packages")
        sys.exit(1)

# =============================================================================
# BASE DE DONNÉES
# =============================================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def charger_activites(conn):
    rows = conn.execute("""
        SELECT id, nom, chemin_dossier
        FROM activite
        WHERE chemin_dossier IS NOT NULL AND chemin_dossier != ''
        ORDER BY nom
    """).fetchall()
    return [dict(r) for r in rows]

# =============================================================================
# EXTRACTION DE TEXTE
# =============================================================================

def extraire_texte_txt(chemin):
    try:
        return chemin.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def extraire_texte_docx(chemin):
    import docx
    try:
        doc = docx.Document(chemin)
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""

def extraire_texte_pdf_natif(chemin):
    import pdfplumber
    import logging
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    try:
        with pdfplumber.open(chemin) as pdf:
            return "\n".join(
                p.extract_text() or "" for p in pdf.pages
            ).strip()
    except Exception:
        return ""

def extraire_texte_pdf_ocr(chemin):
    import pytesseract
    from PIL import Image
    import pdfplumber
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    texte_pages = []
    try:
        with pdfplumber.open(chemin) as pdf:
            for page in pdf.pages:
                img = page.to_image(resolution=200).original
                texte = pytesseract.image_to_string(img, lang="eng+fra")
                texte_pages.append(texte)
        return "\n".join(texte_pages).strip()
    except Exception as e:
        return ""

# =============================================================================
# DÉTECTION DE LANGUE
# =============================================================================

def detecter_langue(texte):
    """Retourne 'en', 'fr', 'inconnu', ou 'trop_court'."""
    from langdetect import detect, DetectorFactory, LangDetectException
    DetectorFactory.seed = 0
    mots = texte.split()
    if len(mots) < SEUIL_MOTS_DETECTION:
        return "trop_court"
    try:
        return detect(texte)
    except LangDetectException:
        return "inconnu"

def classifier_fichier(chemin):
    """
    Retourne (categorie, texte_extrait) où categorie est :
      'anglais'    -> à traduire
      'francais'   -> ignorer
      'trop_court' -> texte trop court pour décider
      'inconnu'    -> autre langue ou détection impossible
      'erreur'     -> exception lors de la lecture
    """
    ext = chemin.suffix.lower()
    try:
        if ext == ".txt":
            texte = extraire_texte_txt(chemin)
        elif ext == ".docx":
            texte = extraire_texte_docx(chemin)
        elif ext == ".pdf":
            texte = extraire_texte_pdf_natif(chemin)
            if len(texte.split()) < SEUIL_MOTS_DETECTION:
                # PDF scanné ou très court : fallback OCR
                texte = extraire_texte_pdf_ocr(chemin)
        else:
            return "non_supporte", ""

        langue = detecter_langue(texte)
        if langue == "en":
            return "anglais", texte
        elif langue == "fr":
            return "francais", texte
        elif langue == "trop_court":
            return "trop_court", texte
        else:
            return "inconnu", texte
    except Exception as e:
        return "erreur", str(e)

# =============================================================================
# TRADUCTION VIA GEMINI
# =============================================================================

def traduire_avec_gemini(nom_activite, texte_source, fichier_source):
    from google import genai
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY_ROM78")
    if not api_key:
        raise RuntimeError("Variable d'environnement GEMINI_API_KEY introuvable.")
    client = genai.Client(api_key=api_key)

    prompt = f"""Tu reçois la fiche descriptive d'une activité pédagogique nature intitulée : « {nom_activite} ».
Le document source est : {fichier_source}

Traduis intégralement ce texte de l'anglais vers le français.
- Conserve la mise en forme (titres, listes, paragraphes).
- Ne résume pas, ne commente pas, traduis tout.
- Si un passage est déjà en français, laisse-le tel quel.
- Réponds uniquement avec le texte traduit, sans préambule ni conclusion.

TEXTE SOURCE :
{texte_source}
"""
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    return response.text.strip()

def sauvegarder_traduction_docx(texte_traduit, chemin_sortie):
    import docx
    doc = docx.Document()
    for ligne in texte_traduit.split("\n"):
        doc.add_paragraph(ligne)
    doc.save(chemin_sortie)

# =============================================================================
# BOUCLE PRINCIPALE
# =============================================================================

def trouver_fichiers_desc(dossier):
    """Retourne les fichiers _DESC_ dans le dossier (extensions cibles uniquement)."""
    resultats = []
    for f in Path(dossier).iterdir():
        if "_DESC_" in f.name and f.suffix.lower() in EXTENSIONS_CIBLES:
            # Ignorer si _DESC_FR_ existe déjà pour cette activité
            resultats.append(f)
    return sorted(resultats)

def desc_fr_existe(dossier):
    """Vérifie si un fichier _DESC_FR_ existe déjà dans le dossier."""
    return any("_DESC_FR_" in f.name for f in Path(dossier).iterdir())

def main():
    verifier_dependances()

    conn = get_db()
    activites = charger_activites(conn)
    conn.close()

    print(f"{'[SIMULATION]' if SIMULATION else '[REEL]'} {len(activites)} activités à parcourir\n")

    stats = {"anglais": 0, "francais": 0, "trop_court": 0,
             "inconnu": 0, "erreur": 0, "deja_traduit": 0,
             "pas_de_desc": 0, "dossier_absent": 0,
             "traduits": 0}
    lignes_rapport = [
        f"Rapport traduction — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Mode : {'SIMULATION' if SIMULATION else 'REEL'}",
        "=" * 60, ""
    ]

    for i, act in enumerate(activites, 1):
        chemin_brut = act["chemin_dossier"] or ""
        if chemin_brut.startswith("file:///"):
            chemin_brut = chemin_brut[len("file:///"):]
        dossier = Path(chemin_brut)
        if not dossier.exists():
            stats["dossier_absent"] += 1
            lignes_rapport.append(f"  [DOSSIER ABSENT] {act['nom']} | {dossier}")
            continue

        # Ignorer si _DESC_FR_ déjà présent pour TOUS les fichiers
        fichiers = trouver_fichiers_desc(dossier)
        if not fichiers:
            stats["pas_de_desc"] += 1
            lignes_rapport.append(f"  [PAS DE DESC] {act['nom']}")
            continue

        print(f"[{i}/{len(activites)}] {act['nom'][:60]} ({len(fichiers)} fichier(s))")

        for fichier in fichiers:
            # Ignorer si la traduction de CE fichier existe déjà
            nom_sortie = fichier.name.replace("_DESC_", "_DESC_FR_").rsplit(".", 1)[0] + ".docx"
            chemin_sortie = dossier / nom_sortie
            if chemin_sortie.exists():
                stats["deja_traduit"] += 1
                lignes_rapport.append(f"  [DEJA TRADUIT] {act['nom']} | {fichier.name}")
                continue

            categorie, texte = classifier_fichier(fichier)
            stats[categorie if categorie in stats else "inconnu"] += 1

            ligne = f"  [{categorie.upper()}] {act['nom']} | {fichier.name}"
            lignes_rapport.append(ligne)

            if categorie == "trop_court":
                lignes_rapport.append(f"    ({len(texte.split())} mots) : {texte[:120]!r}")
            elif categorie == "inconnu":
                lignes_rapport.append(f"    Langue non identifiée : {texte[:120]!r}")
            elif categorie == "erreur":
                lignes_rapport.append(f"    Erreur lecture : {texte[:200]}")

            if categorie != "anglais":
                continue

            if SIMULATION:
                print(f"    -> [SIMULATION] créerait {chemin_sortie.name}")
                lignes_rapport.append(f"    -> créerait {chemin_sortie.name}")
            else:
                try:
                    print(f"    -> Traduction en cours...")
                    traduction = traduire_avec_gemini(act["nom"], texte, fichier.name)
                    sauvegarder_traduction_docx(traduction, chemin_sortie)
                    stats["traduits"] += 1
                    print(f"    -> Sauvegardé : {chemin_sortie.name}")
                    lignes_rapport.append(f"    -> Traduit : {chemin_sortie.name}")
                    time.sleep(DELAI_ENTRE_APPELS)
                except Exception as e:
                    print(f"    -> ERREUR traduction : {e}")
                    lignes_rapport.append(f"    -> ERREUR : {e}")
                    stats["erreur"] += 1

    # Résumé
    lignes_rapport += [
        "", "=" * 60, "RÉSUMÉ",
        f"  Anglais détectés   : {stats['anglais']}",
        f"  Français           : {stats['francais']}",
        f"  Trop court         : {stats['trop_court']}",
        f"  Langue inconnue    : {stats['inconnu']}",
        f"  Déjà traduits      : {stats['deja_traduit']}",
        f"  Sans fichier DESC  : {stats['pas_de_desc']}",
        f"  Dossier absent     : {stats['dossier_absent']}",
        f"  Erreurs            : {stats['erreur']}",
        f"  Traduits ce run    : {stats['traduits']}",
    ]

    rapport = "\n".join(lignes_rapport)
    RAPPORT_PATH.write_text(rapport, encoding="utf-8")
    print("\n" + "=" * 60)
    print(rapport.split("=" * 60)[-1])
    print(f"\nRapport complet : {RAPPORT_PATH}")

if __name__ == "__main__":
    main()
