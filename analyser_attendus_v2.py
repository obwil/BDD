# =============================================================================
# analyser_attendus_v2.py
# =============================================================================
# Pour chaque activite en base avec un fichier _DESC_ :
#   - Envoie le contenu a Gemini
#   - Gemini identifie les attendus pertinents pour un cycle donne (EDD + disc.)
#   - Insere dans activite_attendu et activite_cycle
#   - Marque la progression dans activite_cycle_analysee
#
# Usage : modifier CYCLE = 1 (ou 2 ou 3), puis lancer.
# Prerequis : migration_ajout_suivi_cycle.py et import_attendus_v2.py executes.
# =============================================================================

import base64
import json
import sqlite3
import sys
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "activites.db"
DROPBOX_ACTIVITES = Path(r"C:\Users\moina\Dropbox\Animation\Activites v2")

# =============================================================================
# CONFIGURATION
# =============================================================================

# Cycle a analyser : 1, 2 ou 3
CYCLE = 1

GEMINI_MODEL = "gemini-2.5-flash"
DELAI_ENTRE_APPELS = 15  # secondes entre appels

# None = toutes les activites, ex: 5 = mode test
LIMITE = None

# True = retraiter meme les activites deja dans activite_cycle_analysee pour ce cycle
FORCER_REANALYSE = False

EXTENSIONS_SUPPORTEES = {".pdf", ".jpg", ".jpeg", ".png", ".docx", ".txt"}

SYSTEM_PROMPT = """Tu es un assistant specialise en pedagogie de la nature et en education a l'environnement.
Tu analyses des fiches d'activites pedagogiques nature et tu extrais des informations structurees.
Tu reponds UNIQUEMENT en JSON valide, sans aucun texte autour, sans balises markdown.
"""

# =============================================================================
# BASE DE DONNEES
# =============================================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def charger_attendus_cycle(conn, cycle_id):
    rows = conn.execute("""
        SELECT a.id, a.type, a.domaine, a.sous_domaine, a.libelle, c.code as cycle_code
        FROM attendu_scolaire a
        JOIN cycle c ON c.id = a.cycle_id
        WHERE a.cycle_id = ?
        ORDER BY a.type, a.domaine, a.id
    """, (cycle_id,)).fetchall()
    return [dict(r) for r in rows]


def activites_a_traiter(conn, cycle_id, forcer=False):
    if forcer:
        return [dict(r) for r in conn.execute(
            "SELECT id, nom, chemin_dossier FROM activite ORDER BY nom"
        ).fetchall()]
    else:
        deja = {r[0] for r in conn.execute(
            "SELECT activite_id FROM activite_cycle_analysee WHERE cycle_id = ?",
            (cycle_id,)
        ).fetchall()}
        rows = conn.execute(
            "SELECT id, nom, chemin_dossier FROM activite ORDER BY nom"
        ).fetchall()
        return [dict(r) for r in rows if r["id"] not in deja]


def enregistrer_resultats(conn, activite_id, cycle_id, attendu_ids, ids_valides):
    attendu_ids = [aid for aid in attendu_ids if aid in ids_valides]

    for aid in attendu_ids:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO activite_attendu (activite_id, attendu_id) VALUES (?, ?)",
                (activite_id, aid)
            )
        except Exception as e:
            print(f"    ATTENTION : attendu {aid} : {e}")

    # Cycles derives automatiquement depuis les attendus
    if attendu_ids:
        placeholders = ",".join("?" * len(attendu_ids))
        cycle_ids = [r[0] for r in conn.execute(
            f"SELECT DISTINCT cycle_id FROM attendu_scolaire WHERE id IN ({placeholders})",
            attendu_ids
        ).fetchall()]
        for cid in cycle_ids:
            conn.execute(
                "INSERT OR IGNORE INTO activite_cycle (activite_id, cycle_id) VALUES (?, ?)",
                (activite_id, cid)
            )

    # Marquer comme analysee pour ce cycle
    conn.execute(
        "INSERT OR IGNORE INTO activite_cycle_analysee (activite_id, cycle_id) VALUES (?, ?)",
        (activite_id, cycle_id)
    )
    conn.commit()

# =============================================================================
# LECTURE FICHIERS _DESC_
# =============================================================================

def normaliser_chemin(chemin):
    if chemin and chemin.startswith("file:///"):
        chemin = chemin[8:].replace("/", "\\")
    return chemin


def trouver_fichiers_desc(chemin_dossier):
    if not chemin_dossier:
        return []
    dossier = Path(normaliser_chemin(chemin_dossier))
    if not dossier.exists():
        return []
    return [
        f for f in dossier.iterdir()
        if f.is_file() and f.name.startswith("_DESC_")
        and f.suffix.lower() in EXTENSIONS_SUPPORTEES
    ]


def fichier_vers_contenu_api(fichier):
    ext = fichier.suffix.lower()

    if ext in {".jpg", ".jpeg", ".png"}:
        mt = "image/jpeg" if ext in {".jpg", ".jpeg"} else "image/png"
        data = base64.standard_b64encode(fichier.read_bytes()).decode("utf-8")
        return {"type": "image", "source": {"type": "base64", "media_type": mt, "data": data}}

    if ext == ".pdf":
        data = base64.standard_b64encode(fichier.read_bytes()).decode("utf-8")
        return {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}}

    if ext == ".docx":
        try:
            from docx import Document
            doc = Document(str(fichier))
            texte = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            texte = f"[Erreur lecture DOCX : {e}]"
        return {"type": "text", "text": f"[Contenu du fichier {fichier.name}]\n{texte}"}

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

def construire_prompt(activite_nom, referentiel):
    def fmt_attendu(a):
        sd = f" / {a['sous_domaine']}" if a['sous_domaine'] else ""
        return (f"  id={a['id']}, type={a['type']}, "
                f"domaine={a['domaine']}{sd}, libelle={a['libelle']}")

    ref_text = "\n".join(fmt_attendu(a) for a in referentiel)

    return f"""Tu vas analyser la fiche descriptive de l'activite pedagogique nature intitulee : << {activite_nom} >>.

=== ATTENDUS SCOLAIRES DISPONIBLES (Cycle {CYCLE}) ===
Les attendus sont de deux types :
- type=EDD : attendus d'Education au Developpement Durable
- type=disciplinaire : attendus des programmes disciplinaires (Francais, EPS, Maths, Sciences, etc.)

{ref_text}

=== INSTRUCTIONS ===

En te basant UNIQUEMENT sur le contenu des fichiers fournis, identifie les attendus directement travailles
par cette activite et retourne-les en JSON :

{{
  "attendu_ids": [liste des id d'attendus correspondants]
}}

REGLES :
- Ne propose que des IDs qui existent dans le referentiel fourni ci-dessus.
- Sois TRES selectif : ne retiens que les attendus qui correspondent DIRECTEMENT et PRECISEMENT
  a ce que l'activite fait concretement -- pas a ce qu'elle pourrait theoriquement aborder.
- Un attendu ne doit etre retenu que si un animateur pourrait affirmer sans hesitation que
  l'activite le travaille vraiment.
- Si l'activite est simple et ciblee, 1 ou 2 attendus suffisent.
- Ne retiens jamais un attendu par defaut ou parce qu'il est vaguement lie au theme :
  en cas de doute, ne le retiens pas.
- Maximum 6 attendus au total (EDD + disciplinaires confondus).
- Si aucun attendu ne correspond clairement, retourne un tableau vide [].
- Le JSON doit etre valide et complet. Aucun texte en dehors du JSON.
"""

# =============================================================================
# APPEL GEMINI
# =============================================================================

def _appel_gemini(content):
    import google.generativeai as genai

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT
    )

    parts = []
    for bloc in content:
        if bloc["type"] == "text":
            parts.append(bloc["text"])
        elif bloc["type"] == "image":
            parts.append({"inline_data": {"mime_type": bloc["source"]["media_type"], "data": bloc["source"]["data"]}})
        elif bloc["type"] == "document":
            parts.append({"inline_data": {"mime_type": "application/pdf", "data": bloc["source"]["data"]}})

    response = model.generate_content(parts)
    return response.text.strip()


def analyser_activite(activite_nom, fichiers, referentiel):
    content = [{"type": "text", "text": construire_prompt(activite_nom, referentiel)}]
    for fichier in fichiers:
        bloc = fichier_vers_contenu_api(fichier)
        if bloc:
            content.append({"type": "text", "text": f"\n--- Fichier : {fichier.name} ---"})
            content.append(bloc)

    MAX_RETRIES = 5
    for tentative in range(MAX_RETRIES):
        try:
            raw = _appel_gemini(content)
            break
        except Exception as e:
            msg = str(e)
            is_prohibited = "PROHIBITED_CONTENT" in msg or "prohibited" in msg.lower()
            is_rate = "rate_limit" in msg or "429" in msg or "quota" in msg.lower() or "Resource" in msg
            if is_prohibited:
                print(f"  PROHIBITED_CONTENT : activite marquee analysee (0 attendus).")
                return {"attendu_ids": []}
            if is_rate:
                attente = 60 * (tentative + 1)
                print(f"  Rate limit. Attente {attente}s (tentative {tentative+1}/{MAX_RETRIES})...")
                time.sleep(attente)
                if tentative == MAX_RETRIES - 1:
                    raise
            else:
                raise

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw.strip())

    if isinstance(data, list):
        data = {"attendu_ids": [x.get("attendu_id") for x in data if isinstance(x, dict) and "attendu_id" in x]}

    return data

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print(f"ANALYSE ATTENDUS V2 — CYCLE {CYCLE}")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERREUR : Base SQLite introuvable : {DB_PATH}")
        sys.exit(1)

    import os
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("ERREUR : variable d'environnement GEMINI_API_KEY non definie.")
        sys.exit(1)

    import google.generativeai as genai
    genai.configure(api_key=gemini_key)
    print(f"  API : Google Gemini ({GEMINI_MODEL})")

    conn = get_db()

    # Verifier que la table de suivi existe
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    if "activite_cycle_analysee" not in tables:
        print("ERREUR : table activite_cycle_analysee absente. Lancez migration_ajout_suivi_cycle.py")
        conn.close()
        sys.exit(1)

    # Trouver le cycle_id
    cycle_row = conn.execute("SELECT id FROM cycle WHERE code = ?", (f"C{CYCLE}",)).fetchone()
    if not cycle_row:
        print(f"ERREUR : Cycle C{CYCLE} introuvable en base.")
        conn.close()
        sys.exit(1)
    cycle_id = cycle_row[0]

    print(f"\n Chargement des attendus Cycle {CYCLE}...")
    referentiel = charger_attendus_cycle(conn, cycle_id)
    if not referentiel:
        print(f"ERREUR : Aucun attendu pour C{CYCLE} en base. Lancez import_attendus_v2.py")
        conn.close()
        sys.exit(1)
    ids_valides = {a["id"] for a in referentiel}
    n_edd  = sum(1 for a in referentiel if a["type"] == "EDD")
    n_disc = sum(1 for a in referentiel if a["type"] == "disciplinaire")
    print(f"  {len(referentiel)} attendus charges ({n_edd} EDD, {n_disc} disciplinaires)")

    print(f"\n Recherche des activites a traiter...")
    activites = activites_a_traiter(conn, cycle_id, forcer=FORCER_REANALYSE)

    a_analyser = []
    sans_desc = []
    for act in activites:
        fichiers = trouver_fichiers_desc(act.get("chemin_dossier"))
        if fichiers:
            a_analyser.append((act, fichiers))
        else:
            sans_desc.append(act["nom"])

    print(f"  -> {len(a_analyser)} ont des fichiers _DESC_ a analyser")
    print(f"  -> {len(sans_desc)} n'ont pas de fichier _DESC_ (ignorees)")

    if LIMITE:
        a_analyser = a_analyser[:LIMITE]
        print(f"  Mode test : limite de {LIMITE} activite(s)")

    if not a_analyser:
        print("\nOK Rien a faire.")
        conn.close()
        return

    print(f"\n{'=' * 60}")
    print(f"Debut de l'analyse ({len(a_analyser)} activites, Cycle {CYCLE})...")
    print(f"{'=' * 60}\n")

    succes = 0
    erreurs = 0

    for i, (act, fichiers) in enumerate(a_analyser, 1):
        nom = act["nom"]
        print(f"[{i}/{len(a_analyser)}] {nom}")
        print(f"   Fichiers : {', '.join(f.name for f in fichiers)}")

        try:
            resultats = analyser_activite(nom, fichiers, referentiel)
            attendu_ids = resultats.get("attendu_ids", [])
            if not isinstance(attendu_ids, list):
                attendu_ids = []
            attendu_ids = [int(aid) for aid in attendu_ids if str(aid).isdigit() or isinstance(aid, int)]

            enregistrer_resultats(conn, act["id"], cycle_id, attendu_ids, ids_valides)
            print(f"  OK : {len(attendu_ids)} attendu(s) associe(s)")
            succes += 1

        except Exception as e:
            print(f"  ERREUR : {e}")
            erreurs += 1

        if i < len(a_analyser):
            time.sleep(DELAI_ENTRE_APPELS)
        print()

    conn.close()

    print("=" * 60)
    print(f"Termine : {succes} succes, {erreurs} erreur(s)")
    print(f"Relancez avec CYCLE = {CYCLE} et FORCER_REANALYSE = False pour les erreurs.")
    print(f"Changez CYCLE = {CYCLE+1 if CYCLE < 3 else 1} pour le cycle suivant.")
    print("=" * 60)


if __name__ == "__main__":
    main()
