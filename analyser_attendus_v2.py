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
LIMITE = 3

# True = retraiter meme les activites deja dans activite_cycle_analysee pour ce cycle
FORCER_REANALYSE = False

EXTENSIONS_SUPPORTEES = {".pdf", ".jpg", ".jpeg", ".png", ".docx", ".txt"}

SYSTEM_PROMPT = """Tu es un assistant specialise en pedagogie de la nature, en education a l'environnement et en developpement de l'enfant.
Tu analyses des fiches d'activites pedagogiques nature pour evaluer leur pertinence selon le cycle scolaire et extraire des informations structurees.
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

    profils_cycle = {
        "1": {
            "label": "3-6 ans (maternelle / Cycle 1)",
            "peut": [
                "Observer, manipuler, explorer avec les sens (toucher, voir, ecouter, sentir, gouter)",
                "S'exprimer oralement et raconter",
                "Imiter, mimer, jouer a faire semblant (jeu symbolique a son apogee)",
                "Participer a des jeux simples avec des regles orales courtes",
                "Dessiner, peindre, modelager, construire avec des materiaux",
                "Reconnaitre et nommer des elements naturels observes directement",
                "Se deplacer dans des environnements varies (courir, sauter, grimper)",
                "Cooperer dans de petits groupes avec accompagnement adulte",
                "Formuler des questions simples (stade du 'pourquoi ?')",
                "Comprendre des consignes orales simples",
            ],
            "ne_peut_pas": [
                "Lire de maniere autonome (ne sait pas encore lire)",
                "Ecrire de maniere autonome (premiers essais seulement vers 5-6 ans)",
                "Comprendre des concepts abstraits (statistiques, geopolitique, cycles biogeochimiques)",
                "Raisonner sur plusieurs criteres simultanement (pensee centree sur un seul aspect)",
                "Analyser des documents ecrits, des graphiques ou des tableaux",
                "Mener une demarche d'investigation autonome avec hypotheses",
                "Comprendre des relations cause-effet complexes et distantes",
                "Repondre a des QCM ecrits ou suivre des reglements de jeu ecrits complexes",
                "Calculer, compter au-dela de 10-20, realiser des operations",
            ],
            "pensee": "Pensee preoperatoire (Piaget) : egocentrique, magique, animiste, centree sur le concret immediat et l'observation sensorielle directe. Le jeu symbolique est dominant.",
        },
        "2": {
            "label": "6-9 ans (CP, CE1, CE2 / Cycle 2)",
            "peut": [
                "Lire des textes simples (acquisition progressive de la lecture au CP)",
                "Ecrire des textes courts avec aide",
                "Suivre des regles de jeu ecrites simples",
                "Raisonner sur des situations concretes et manipulables",
                "Comparer, classer, ordonner des objets selon plusieurs criteres",
                "Mener de petites investigations simples avec guidage",
                "Comprendre des relations cause-effet directes et observables",
                "Cooperer en equipe avec des roles definis",
                "Utiliser un vocabulaire scientifique de base",
                "Realiser des dessins d'observation, des croquis simples",
                "Comprendre les saisons, le cycle de l'eau, les chaines alimentaires simples",
            ],
            "ne_peut_pas": [
                "Lire et analyser des documents complexes de maniere autonome (surtout en debut de cycle)",
                "Mener une demarche scientifique completement autonome",
                "Comprendre des statistiques, pourcentages, donnees chiffrees complexes",
                "Argumenter avec des sources multiples",
                "Realiser des syntheses ecrites elaborees",
                "Aborder des enjeux geopolitiques mondiaux ou des concepts tres abstraits",
                "Comprendre des echelles de temps geologiques ou des mecanismes systemiques complexes",
            ],
            "pensee": "Pensee des operations concretes (Piaget) : reversibilite, decentration, conservation. Raisonnement inductif a partir du concret. Debut du travail ecrit autonome.",
        },
        "3": {
            "label": "9-12 ans (CM1, CM2, 6e / Cycle 3)",
            "peut": [
                "Lire et comprendre des textes documentaires de maniere autonome",
                "Rediger des textes structures et argumentes",
                "Mener une demarche d'investigation complete (hypothese, experimentation, conclusion)",
                "Analyser des documents (textes, cartes, graphiques, images)",
                "Raisonner de maniere abstraite et sur plusieurs criteres simultanes",
                "Comprendre des relations systemiques et des mecanismes complexes",
                "Argumenter, debattre, justifier un point de vue",
                "Utiliser des outils de mesure et de representation (boussole, thermometre, carte)",
                "Situer des phenomenes dans le temps long (histoire, temps geologiques)",
                "Comprendre des enjeux a differentes echelles (local, national, mondial)",
                "Distinguer fait scientifique et opinion",
                "Travailler en autonomie sur des projets de longue duree",
            ],
            "ne_peut_pas": [
                "Mener des raisonnements hypothetico-deductifs purs et abstraits (commence a emerger seulement)",
                "Apprehender des enjeux geopolitiques tres complexes sans ancrage concret",
            ],
            "pensee": "Debut des operations formelles (Piaget) : pensee abstraite emergente, esprit critique, capacite a raisonner sur des possibles. Autonomie croissante dans les apprentissages.",
        },
    }

    profil = profils_cycle.get(str(CYCLE), {})
    label = profil.get("label", f"Cycle {CYCLE}")
    peut = "\n".join(f"  + {x}" for x in profil.get("peut", []))
    ne_peut_pas = "\n".join(f"  - {x}" for x in profil.get("ne_peut_pas", []))
    pensee = profil.get("pensee", "")

    return f"""Tu vas analyser la fiche descriptive de l'activite pedagogique nature intitulee : << {activite_nom} >>.

=== PROFIL DEVELOPPEMENT : {label} ===

Ce que les enfants de ce cycle PEUVENT faire :
{peut}

Ce que les enfants de ce cycle NE PEUVENT PAS faire ou NE SAVENT PAS encore :
{ne_peut_pas}

Stade cognitif : {pensee}

=== ATTENDUS SCOLAIRES DISPONIBLES (Cycle {CYCLE}) ===
Les attendus sont de deux types :
- type=EDD : attendus d'Education au Developpement Durable
- type=disciplinaire : attendus des programmes disciplinaires (Francais, EPS, Maths, Sciences, etc.)

{ref_text}

=== INSTRUCTIONS ===

ETAPE 1 — VERIFIER LA PERTINENCE DU CYCLE
En te basant sur le profil developpement ci-dessus, analyse precisement CE QUE L'ENFANT
DOIT FAIRE CONCRETEMENT dans cette activite (pas le theme general, pas le format de la fiche).

METHODE : identifie les mecaniques concretes de l'activite :
- L'enfant doit-il lire des cartes, des consignes ecrites, des QCM ?
- L'enfant doit-il ecrire, noter, remplir quelque chose ?
- L'enfant doit-il comprendre des statistiques, pourcentages, donnees chiffrees ?
- L'enfant doit-il raisonner de maniere abstraite sur des concepts complexes ?
- L'enfant doit-il suivre des regles de jeu ecrites et complexes ?

PRINCIPE FONDAMENTAL :
Le format ou l'etiquette d'une activite (jeu, atelier, sortie, conte, manipulation...)
ne garantit pas son adaptation au cycle. Seules les mecaniques concretes que l'enfant
doit realiser permettent de juger. Une meme etiquette peut designer des activites
adaptees ou inadaptees selon ce que l'enfant fait reellement.

Retourne immediatement {{"attendu_ids": []}} si l'activite necessite que l'enfant :
- Lise des textes, cartes ou consignes ecrites de maniere autonome (pour C1)
- Reponde a des QCM ecrits ou des questions sur cartes a lire (pour C1)
- Comprenne des statistiques, pourcentages ou donnees geographiques/economiques (pour C1 et C2 jeune)
- Raisonne sur des concepts systemiques abstraits hors de portee du stade cognitif
- Suive des regles de jeu ecrites complexes en lisant lui-meme (pour C1)

Attention : le fait que la FICHE soit ecrite en langage adulte ne signifie pas que l'ACTIVITE
est inadaptee. C'est ce que l'enfant fait concretement qui compte, pas le langage de la fiche.

FORMAT DE REPONSE OBLIGATOIRE :
Tu dois repondre en deux blocs dans cet ordre exact :

BLOC 1 — RAISONNEMENT (texte libre, 3 a 5 phrases maximum) :
Decris en quelques phrases :
1. Ce que l'enfant fait concretement dans cette activite (mecaniques reelles)
2. Pourquoi c'est adapte ou inadapte au Cycle {CYCLE} ({label})
3. Ta conclusion : adapte ou inadapte

BLOC 2 — JSON (obligatoire, meme si le tableau est vide) :
```json
{{"attendu_ids": [liste des id ou tableau vide]}}
```

REGLES pour le BLOC 2 :
- Ne propose que des IDs qui existent dans le referentiel fourni ci-dessus.
- Si l'activite est inadaptee au cycle (conclu dans le BLOC 1), retourne {{"attendu_ids": []}}.
- Sois TRES selectif : ne retiens que les attendus qui correspondent DIRECTEMENT et PRECISEMENT
  a ce que l'activite fait concretement -- pas a ce qu'elle pourrait theoriquement aborder.
- Un attendu ne doit etre retenu que si un animateur pourrait affirmer sans hesitation que
  l'activite le travaille vraiment.
- Si l'activite est simple et ciblee, 1 ou 2 attendus suffisent.
- Ne retiens jamais un attendu par defaut ou parce qu'il est vaguement lie au theme :
  en cas de doute, ne le retiens pas.
- Maximum 10 attendus au total (EDD + disciplinaires confondus).
- Si aucun attendu ne correspond clairement, retourne {{"attendu_ids": []}}.
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

    import re as _re

    log_path = Path(__file__).parent / 'analyse_raisonnements.log'
    raisonnement = ''
    data = None

    if '```json' in raw:
        parties = raw.split('```json')
        raisonnement = parties[0].strip()
        json_str = parties[1].split('```')[0].strip()
        try:
            data = json.loads(json_str)
        except Exception:
            data = {'attendu_ids': []}
    elif '```' in raw:
        parties = raw.split('```')
        raisonnement = parties[0].strip()
        partie = parties[1]
        if partie.startswith('json'):
            partie = partie[4:]
        try:
            data = json.loads(partie.strip())
        except Exception:
            data = {'attendu_ids': []}
    else:
        try:
            data = json.loads(raw.strip())
        except Exception:
            data = {'attendu_ids': []}
            raisonnement = raw.strip()

    if not raisonnement and isinstance(data, dict):
        raisonnement = str(data.get('raisonnement', '') or data.get('reasoning', ''))

    for prefix in ['BLOC 1 - RAISONNEMENT', 'BLOC 1 — RAISONNEMENT', 'BLOC 1', 'RAISONNEMENT']:
        if raisonnement.upper().startswith(prefix):
            raisonnement = raisonnement[len(prefix):].strip().lstrip('-— ').strip()
            break

    if raisonnement:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write('\n=== ' + activite_nom + ' ===\n')
            f.write(raisonnement + '\n')

    if not isinstance(data, dict):
        data = {'attendu_ids': []}
    if isinstance(data, list):
        data = {'attendu_ids': [x.get('attendu_id') for x in data if isinstance(x, dict) and 'attendu_id' in x]}

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
