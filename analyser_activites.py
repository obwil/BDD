# =============================================================================
# analyser_activites.py
# =============================================================================
# Pour chaque dossier d'activité dans le répertoire Dropbox :
#   - Cherche les fichiers _DESC_* (pdf, docx, txt, jpg, jpeg, png)
#   - Ignore les activités déjà analysées (description IS NOT NULL)
#   - Envoie les fichiers à l'API Claude pour extraction structurée
#   - Enregistre les résultats en base SQLite
#
# Prérequis :
#   pip install anthropic google-generativeai python-docx pillow --break-system-packages
#
# Lancer avec : python analyser_activites.py
# =============================================================================

import base64
import json
import sqlite3
import sys
import time
from pathlib import Path

import argparse

# API choisie selon la variable API_PROVIDER
# Les imports se font dynamiquement dans main()

# =============================================================================
# CONFIGURATION
# =============================================================================

DROPBOX_ACTIVITES = Path(r"C:\Users\moina\Dropbox\Animation\Activités v2")
DB_PATH = Path(__file__).parent / "activites.db"
# =============================================================================
# CHOIX DE L'API
# =============================================================================
# "claude" : utilise l'API Anthropic (clé ANTHROPIC_API_KEY)
# "gemini" : utilise l'API Google Gemini (clé GEMINI_API_KEY)
API_PROVIDER = "gemini"

CLAUDE_MODEL  = "claude-haiku-4-5-20251001"
GEMINI_MODEL  = "gemini-2.5-flash"

# Délai entre deux appels API (secondes) — évite le rate limiting
DELAI_ENTRE_APPELS = 15

# Nombre maximum d'activités à analyser par lancement.
# Mettre None pour analyser toutes les activités sans description.
# Exemple : LIMITE = 10 pour tester sur 10 activités.
LIMITE = None

# Si True, réanalyse même les activités déjà traitées (description non nulle).
# Utile pour corriger les premières analyses qui n'avaient pas les cycles.
FORCER_REANALYSE = False

# Activer ou désactiver l'analyse des pédagogies et théories d'apprentissage.
# Désactiver réduit la taille du prompt et le nombre de tokens consommés.
ANALYSER_PEDAGOGIES = False
ANALYSER_THEORIES = False

# Extensions supportées pour les fichiers _DESC_
EXTENSIONS_SUPPORTEES = {".pdf", ".jpg", ".jpeg", ".png", ".docx", ".txt"}

# =============================================================================
# BASE DE DONNÉES
# =============================================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def charger_referentiels(conn):
    """Charge tous les référentiels pour les inclure dans le prompt."""
    def flatten_tree(table):
        rows = conn.execute(
            f"SELECT id, nom, niveau, parent_id FROM {table} ORDER BY niveau, nom"
        ).fetchall()
        return [dict(r) for r in rows]

    return {
        "thematiques": flatten_tree("thematique"),
        "objectifs": flatten_tree("objectif"),
        "pedagogies": [dict(r) for r in conn.execute(
            "SELECT id, nom FROM pedagogie ORDER BY nom"
        ).fetchall()] if ANALYSER_PEDAGOGIES else [],
        "theories": [dict(r) for r in conn.execute(
            "SELECT id, nom FROM theorie_apprentissage ORDER BY nom"
        ).fetchall()] if ANALYSER_THEORIES else [],
        "cycles": [dict(r) for r in conn.execute(
            "SELECT id, code, nom, ages FROM cycle ORDER BY id"
        ).fetchall()],
        "attendus": [dict(r) for r in conn.execute(
            "SELECT id, cycle_id, domaine, sous_domaine, libelle FROM attendu_scolaire ORDER BY cycle_id, domaine"
        ).fetchall()],
    }


def supprimer_parents_redondants(conn, ids, table):
    """
    Étant donné une liste d'IDs de thématiques ou objectifs,
    supprime ceux qui sont ancêtres d'un autre ID déjà dans la liste.
    """
    if len(ids) <= 1:
        return ids

    # Récupérer tous les parent_id pour construire l'arbre
    rows = conn.execute(f"SELECT id, parent_id FROM {table}").fetchall()
    parent_of = {r[0]: r[1] for r in rows}  # id -> parent_id

    def ancetres(nid):
        """Retourne tous les ancêtres d'un nœud."""
        result = set()
        p = parent_of.get(nid)
        while p is not None:
            result.add(p)
            p = parent_of.get(p)
        return result

    # Calculer tous les ancêtres de chaque ID sélectionné
    tous_ancetres = set()
    for nid in ids:
        tous_ancetres |= ancetres(nid)

    # Garder uniquement les IDs qui ne sont pas ancêtres d'un autre ID sélectionné
    return [nid for nid in ids if nid not in tous_ancetres]


def activites_a_traiter(conn, forcer=False):
    """Retourne les activités qui ont un chemin valide et pas encore de description."""
    condition = "" if forcer else "AND description IS NULL"
    rows = conn.execute(f"""
        SELECT id, nom, chemin_dossier
        FROM activite
        WHERE chemin_dossier IS NOT NULL
          AND chemin_dossier != ''
          {condition}
        ORDER BY nom
    """).fetchall()
    return [dict(r) for r in rows]


def enregistrer_resultats(conn, activite_id, resultats):
    """Enregistre les résultats de l'analyse en base."""
    # Mise à jour des champs directs
    conn.execute("""
        UPDATE activite SET
            description     = ?,
            objectif_texte  = ?,
            format_groupe   = ?,
            duree_min       = ?,
            meteo_soleil    = ?,
            meteo_pluie     = ?,
            meteo_vent      = ?,
            meteo_nuage     = ?,
            meteo_nuit      = ?
        WHERE id = ?
    """, (
        resultats.get("description"),
        resultats.get("objectif_texte"),
        resultats.get("format_groupe"),
        resultats.get("duree_min"),
        1 if resultats.get("meteo_soleil") else 0,
        1 if resultats.get("meteo_pluie") else 0,
        1 if resultats.get("meteo_vent") else 0,
        1 if resultats.get("meteo_nuage") else 0,
        1 if resultats.get("meteo_nuit") else 0,
        activite_id,
    ))

    # Relations many-to-many (avec nettoyage des parents redondants)
    thematique_ids = supprimer_parents_redondants(conn, resultats.get("thematique_ids", []), "thematique")
    objectif_ids   = supprimer_parents_redondants(conn, resultats.get("objectif_ids", []), "objectif")
    _inserer_relations(conn, activite_id, "activite_thematique", "thematique_id", thematique_ids)
    _inserer_relations(conn, activite_id, "activite_objectif", "objectif_id", objectif_ids)
    _inserer_relations(conn, activite_id, "activite_pedagogie", "pedagogie_id",
                       resultats.get("pedagogie_ids", []))
    _inserer_relations(conn, activite_id, "activite_theorie", "theorie_id",
                       resultats.get("theorie_ids", []))

    # Attendus scolaires
    attendu_ids = resultats.get("attendu_ids", [])
    _inserer_relations(conn, activite_id, "activite_attendu", "attendu_id", attendu_ids)

    # Cycles : derives automatiquement depuis les attendus selectionnes
    if attendu_ids:
        cycle_ids_derives = [
            row[0] for row in conn.execute(
                "SELECT DISTINCT cycle_id FROM attendu_scolaire WHERE id IN ({})".format(
                    ",".join("?" * len(attendu_ids))
                ),
                attendu_ids
            ).fetchall()
        ]
    else:
        cycle_ids_derives = resultats.get("cycle_ids", [])
    _inserer_relations(conn, activite_id, "activite_cycle", "cycle_id", cycle_ids_derives)

    conn.commit()


def _inserer_relations(conn, activite_id, table, fk_col, ids):
    for fk_id in ids:
        try:
            conn.execute(
                f"INSERT OR IGNORE INTO {table} (activite_id, {fk_col}) VALUES (?, ?)",
                (activite_id, fk_id)
            )
        except Exception as e:
            print(f"    ATTENTION :  Relation {table} id={fk_id} : {e}")

# =============================================================================
# LECTURE DES FICHIERS _DESC_
# =============================================================================

def normaliser_chemin(chemin_dossier):
    """Convertit un chemin file:/// en chemin Windows utilisable."""
    if chemin_dossier.startswith("file:///"):
        chemin_dossier = chemin_dossier[8:].replace("/", "\\")
    return chemin_dossier


def trouver_fichiers_desc(chemin_dossier):
    """Retourne la liste des fichiers _DESC_ dans le dossier d'activite."""
    dossier = Path(normaliser_chemin(chemin_dossier))
    if not dossier.exists():
        return []
    fichiers = []
    for f in dossier.iterdir():
        if f.is_file() and f.name.startswith("_DESC_") and f.suffix.lower() in EXTENSIONS_SUPPORTEES:
            fichiers.append(f)
    return fichiers


def fichier_vers_contenu_api(fichier: Path):
    """
    Convertit un fichier en bloc de contenu pour l'API Claude.
    Retourne un dict prêt à insérer dans messages[].content[].
    """
    ext = fichier.suffix.lower()

    # ---- Images ----
    if ext in {".jpg", ".jpeg", ".png"}:
        media_type = "image/jpeg" if ext in {".jpg", ".jpeg"} else "image/png"
        data = base64.standard_b64encode(fichier.read_bytes()).decode("utf-8")
        return {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": data}
        }

    # ---- PDF ----
    if ext == ".pdf":
        data = base64.standard_b64encode(fichier.read_bytes()).decode("utf-8")
        return {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": data}
        }

    # ---- DOCX ----
    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(str(fichier))
            texte = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            texte = f"[Erreur lecture DOCX : {e}]"
        return {"type": "text", "text": f"[Contenu du fichier {fichier.name}]\n{texte}"}

    # ---- TXT ----
    if ext == ".txt":
        try:
            texte = fichier.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            texte = f"[Erreur lecture TXT : {e}]"
        return {"type": "text", "text": f"[Contenu du fichier {fichier.name}]\n{texte}"}

    return None

# =============================================================================
# PROMPT
# =============================================================================

SYSTEM_PROMPT = """Tu es un assistant spécialisé en pédagogie de la nature et en éducation à l'environnement.
Tu analyses des fiches d'activités pédagogiques nature et tu extrais des informations structurées.
Tu réponds UNIQUEMENT en JSON valide, sans aucun texte autour, sans balises markdown.
"""

def construire_prompt(activite_nom, referentiels):
    """Construit le prompt utilisateur avec les référentiels."""

    def format_liste(items, champs):
        lignes = []
        for item in items:
            parts = [f"id={item['id']}"]
            for c in champs:
                if c in item and item[c] is not None:
                    parts.append(f"{c}={item[c]}")
            lignes.append("  " + ", ".join(parts))
        return "\n".join(lignes)

    ped_section = f"""PÉDAGOGIES :\n{format_liste(referentiels['pedagogies'], ['nom'])}\n\n""" if ANALYSER_PEDAGOGIES else ""
    theo_section = f"""THÉORIES D'APPRENTISSAGE :\n{format_liste(referentiels['theories'], ['nom'])}\n\n""" if ANALYSER_THEORIES else ""
    ref_text = f"""
=== RÉFÉRENTIELS DISPONIBLES ===

THÉMATIQUES (arbre hiérarchique, niveau 0 = racine) :
{format_liste(referentiels['thematiques'], ['nom', 'niveau'])}

OBJECTIFS (arbre hiérarchique) :
{format_liste(referentiels['objectifs'], ['nom', 'niveau'])}

{ped_section}{theo_section}CYCLES :
{format_liste(referentiels['cycles'], ['code', 'nom', 'ages'])}

ATTENDUS SCOLAIRES EDD (id, cycle_id, domaine, sous_domaine, libelle) :
{format_liste(referentiels['attendus'], ['cycle_id', 'domaine', 'sous_domaine', 'libelle'])}
"""


    ped_json = '  "pedagogie_ids": [liste des id de pédagogies mobilisées. Maximum 3.],\n' if ANALYSER_PEDAGOGIES else ''
    theo_json = '  "theorie_ids": [liste des id de théories d\'apprentissage sous-jacentes. Maximum 2.],\n' if ANALYSER_THEORIES else ''

    prompt = f"""Tu vas analyser la fiche descriptive de l'activité pédagogique nature intitulée : « {activite_nom} ».

{ref_text}

=== INSTRUCTIONS ===

En te basant UNIQUEMENT sur le contenu des fichiers fournis, extrais les informations suivantes et retourne-les en JSON :

{{
  "description": "Résumé concis de l'activité en 2-4 phrases (ce qu'on fait concrètement, le contexte). En français.",
  "objectif_texte": "Objectif pédagogique principal en 1-2 phrases. En français.",
  "format_groupe": "Une valeur parmi : individuel / binôme / petit groupe / grand groupe. Null si non déterminable.",
  "duree_min": "Durée estimée en minutes (entier). Null si non déterminable.",
  "meteo_soleil": true/false — true UNIQUEMENT si l'activité nécessite absolument le soleil (ex: observer les ombres, sécher des objets au soleil). False si le soleil est juste agréable ou si l'activité est en intérieur.,
  "meteo_pluie": true/false — true UNIQUEMENT si l'activité nécessite absolument la pluie (ex: observer les vers de terre, étudier le ruissellement). False sinon.,
  "meteo_vent": true/false — true UNIQUEMENT si l'activité nécessite absolument le vent (ex: fabriquer une girouette, observer la dispersion des graines par le vent). False sinon.,
  "meteo_nuage": true/false — true UNIQUEMENT si l'activité nécessite absolument un ciel nuageux. False sinon.,
  "meteo_nuit": true/false — true UNIQUEMENT si l'activité se déroule obligatoirement de nuit (observation des étoiles, comportements nocturnes, etc.). False sinon.,
  "thematique_ids": [liste des id de thématiques correspondantes — choisis les plus précises (feuilles de l'arbre). Maximum 5.],
  "objectif_ids": [liste des id d'objectifs correspondants — choisis les plus précis. Maximum 3.],
{ped_json}{theo_json}
  "cycle_ids": [liste des id de cycles scolaires visés. Maximum 4.],
  "attendu_ids": [liste des id d'attendus scolaires EDD correspondants. Maximum 4 — mais 1 ou 2 suffisent si l'activité est ciblée. Ne complète pas pour atteindre ce maximum.]
}}

RÈGLES :
- Ne propose que des IDs qui existent dans les référentiels fournis ci-dessus.
- Si une information n'est pas déterminable depuis les fichiers, utilise null ou [].
- Pour les attendus : sois très sélectif. Ne retiens que les attendus qui correspondent DIRECTEMENT et PRÉCISÉMENT à ce que l'activité fait concrètement — pas à ce qu'elle pourrait théoriquement aborder. Un attendu ne doit être retenu que si un animateur pourrait affirmer sans hésitation que l'activité le travaille. Si l'activité est simple et ciblée, 1 ou 2 attendus suffisent. Ne retiens jamais un attendu par défaut ou parce qu'il est vaguement lié au thème : en cas de doute, ne le retiens pas.
- Pour la météo : une condition météo est à true SEULEMENT si l'activité est IMPOSSIBLE ou perd son sens sans cette météo. Le simple fait de se dérouler en extérieur ne justifie pas de cocher soleil ou vent. Exemples où meteo_soleil=true : observer les ombres, étudier les zones lumière/ombre, faire du land art avec les ombres, sécher des objets au soleil, observer le reflet du soleil sur l'eau. Exemple où meteo_soleil=false : sortie nature générale par beau temps, activité en intérieur qui mentionne le soleil en passant. Sois très restrictif pour vent et nuage.
- Pour les thématiques et objectifs : choisis les nœuds les plus précis possible. Ne sélectionne JAMAIS un nœud parent ET l'un de ses descendants en même temps — si tu retiens un enfant, inutile de retenir son parent. Les thématiques choisies doivent permettre de saisir avec précision les contenus abordés.
- Le JSON doit être valide et complet. Aucun texte en dehors du JSON.
"""
    return prompt

# =============================================================================
# ANALYSE VIA CLAUDE API
# =============================================================================

def _appel_claude(client, content):
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}]
    )
    return response.content[0].text.strip()


def _appel_gemini(client, content):
    """Convertit le format Anthropic vers Gemini et appelle l'API."""
    import google.generativeai as genai

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT
    )

    # Convertir les blocs Anthropic en parties Gemini
    parts = []
    for bloc in content:
        if bloc["type"] == "text":
            parts.append(bloc["text"])
        elif bloc["type"] == "image":
            import base64 as b64mod
            parts.append({
                "inline_data": {
                    "mime_type": bloc["source"]["media_type"],
                    "data": bloc["source"]["data"]
                }
            })
        elif bloc["type"] == "document":
            # PDF
            parts.append({
                "inline_data": {
                    "mime_type": "application/pdf",
                    "data": bloc["source"]["data"]
                }
            })

    response = model.generate_content(parts)
    return response.text.strip()


def analyser_activite(client, activite_nom, fichiers, referentiels):
    """
    Envoie les fichiers _DESC_ à Claude et retourne le dict de résultats.
    """
    # Construire le contenu du message
    content = []

    # Ajouter le prompt texte
    content.append({"type": "text", "text": construire_prompt(activite_nom, referentiels)})

    # Ajouter les fichiers
    for fichier in fichiers:
        bloc = fichier_vers_contenu_api(fichier)
        if bloc:
            content.append({"type": "text", "text": f"\n--- Fichier : {fichier.name} ---"})
            content.append(bloc)

    # Appel API avec retry sur rate limit
    MAX_RETRIES = 5
    for tentative in range(MAX_RETRIES):
        try:
            if API_PROVIDER == "gemini":
                raw = _appel_gemini(client, content)
            else:
                raw = _appel_claude(client, content)
            break
        except Exception as e:
            msg = str(e)
            if "rate_limit" in msg or "429" in msg or "quota" in msg.lower() or "Resource" in msg:
                attente = 60 * (tentative + 1)
                print(f"  Rate limit atteint. Attente {attente}s (tentative {tentative+1}/{MAX_RETRIES})...")
                time.sleep(attente)
                if tentative == MAX_RETRIES - 1:
                    raise
            else:
                raise

    # Parser le JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Tentative de nettoyage
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())

# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Analyse des activités via Claude API")
    parser.add_argument("--limit", type=int, default=None,
                        help="Nombre maximum d'activités à analyser (ex: --limit 10)")
    args = parser.parse_args()

    print("=" * 60)
    print("ANALYSE DES ACTIVITÉS VIA CLAUDE API")
    if args.limit:
        print(f"Mode test : limite de {args.limit} activité(s) (argument ligne de commande)")
    elif LIMITE:
        print(f"Mode test : limite de {LIMITE} activité(s) (variable LIMITE dans le script)")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERREUR : Base SQLite introuvable : {DB_PATH}")
        print("   Lancez d'abord create_schema.py")
        sys.exit(1)

    if not DROPBOX_ACTIVITES.exists():
        print(f"ERREUR : Répertoire Dropbox introuvable : {DROPBOX_ACTIVITES}")
        sys.exit(1)

    conn = get_db()
    if API_PROVIDER == "gemini":
        import google.generativeai as genai
        import os
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            print("ERREUR : variable d'environnement GEMINI_API_KEY non définie.")
            sys.exit(1)
        genai.configure(api_key=gemini_key)
        client = genai  # on passe le module, _appel_gemini crée le modèle lui-même
        print(f"  API : Google Gemini ({GEMINI_MODEL})")
    else:
        import anthropic as _anthropic
        client = _anthropic.Anthropic()
        print(f"  API : Anthropic Claude ({CLAUDE_MODEL})")

    print("\n Chargement des référentiels...")
    referentiels = charger_referentiels(conn)
    infos = [f"{len(referentiels['thematiques'])} thématiques",
              f"{len(referentiels['objectifs'])} objectifs",
              f"{len(referentiels['cycles'])} cycles"]
    if ANALYSER_PEDAGOGIES: infos.append(f"{len(referentiels['pedagogies'])} pédagogies")
    if ANALYSER_THEORIES:   infos.append(f"{len(referentiels['theories'])} théories")
    print("  " + ", ".join(infos))

    print("\n Recherche des activités à traiter...")
    activites = activites_a_traiter(conn, forcer=FORCER_REANALYSE)
    print(f"  {len(activites)} activité(s) sans description en base")

    # Filtrer celles qui ont des fichiers _DESC_
    a_analyser = []
    sans_desc = []
    for act in activites:
        fichiers = trouver_fichiers_desc(act["chemin_dossier"])
        if fichiers:
            a_analyser.append((act, fichiers))
        else:
            sans_desc.append(act["nom"])

    print(f"  -> {len(a_analyser)} ont des fichiers _DESC_ à analyser")
    print(f"  -> {len(sans_desc)} n'ont pas de fichier _DESC_ (ignorées)")

    limite = args.limit if args.limit is not None else LIMITE
    if limite:
        a_analyser = a_analyser[:limite]

    if not a_analyser:
        print("\nOK Rien à faire.")
        conn.close()
        return

    print(f"\n{'=' * 60}")
    print(f"Début de l'analyse ({len(a_analyser)} activités)...")
    print(f"{'=' * 60}\n")

    succes = 0
    erreurs = 0

    for i, (act, fichiers) in enumerate(a_analyser, 1):
        nom = act["nom"]
        print(f"[{i}/{len(a_analyser)}] {nom}")
        print(f"   Fichiers : {', '.join(f.name for f in fichiers)}")

        try:
            resultats = analyser_activite(client, nom, fichiers, referentiels)
            enregistrer_resultats(conn, act["id"], resultats)

            print(f"  OK Enregistré")
            if resultats.get("description"):
                preview = resultats["description"][:80].replace("\n", " ")
                print(f"   {preview}…")
            if resultats.get("thematique_ids"):
                print(f"    {len(resultats.get('thematique_ids', []))} thématique(s), {len(resultats.get('attendu_ids', []))} attendu(s)")
            succes += 1

        except Exception as e:
            print(f"  ERREUR : Erreur : {e}")
            erreurs += 1

        # Délai pour éviter le rate limiting
        if i < len(a_analyser):
            time.sleep(DELAI_ENTRE_APPELS)

        print()

    conn.close()

    print("=" * 60)
    print(f"Terminé : {succes} succès, {erreurs} erreur(s)")
    print("=" * 60)


if __name__ == "__main__":
    main()
