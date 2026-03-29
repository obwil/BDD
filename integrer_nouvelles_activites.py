# =============================================================================
# integrer_nouvelles_activites.py
# =============================================================================
# Scanne le dossier Activites v2, detecte les dossiers absents de la BDD,
# et pour chacun ayant un fichier _DESC_ :
#   1. Insere l'activite en BDD (nom = nom du dossier, chemin_dossier)
#   2. Analyse via IA : description, meteo, thematiques, objectifs (etape A)
#   3. Analyse via IA : attendus scolaires C1, C2, C3 (etape B)
#
# =============================================================================

import base64
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

DROPBOX_ACTIVITES = Path(r"C:\Users\moina\Dropbox\Animation\Activites v2")
DB_PATH = Path(__file__).parent / "activites.db"

# "gemini" ou "claude"
API_PROVIDER = "gemini"

GEMINI_MODEL = "gemini-2.5-flash"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

DELAI_ENTRE_APPELS = 20  # secondes entre appels API

# None = tout traiter, ex: 3 = mode test
LIMITE = None

# Extensions supportees pour les fichiers _DESC_
EXTENSIONS_SUPPORTEES = {".pdf", ".jpg", ".jpeg", ".png", ".docx", ".txt"}

# Prefixes de dossiers a ignorer (dossiers de groupes)
PREFIXES_IGNORES = {"_"}

# =============================================================================
# BASE DE DONNEES
# =============================================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def noms_activites_en_bdd(conn):
    rows = conn.execute("SELECT nom FROM activite").fetchall()
    return {r["nom"] for r in rows}


def inserer_activite(conn, nom, chemin_dossier):
    cur = conn.execute(
        "INSERT INTO activite (nom, chemin_dossier) VALUES (?, ?)",
        (nom, str(chemin_dossier))
    )
    conn.commit()
    return cur.lastrowid


def charger_referentiels(conn):
    def flatten(table):
        rows = conn.execute(
            f"SELECT id, nom, niveau, parent_id FROM {table} ORDER BY niveau, nom"
        ).fetchall()
        return [dict(r) for r in rows]

    return {
        "thematiques": flatten("thematique"),
        "objectifs":   flatten("objectif"),
        "cycles":      [dict(r) for r in conn.execute(
            "SELECT id, code, nom, ages FROM cycle ORDER BY id"
        ).fetchall()],
    }


def charger_attendus_cycle(conn, cycle_id):
    rows = conn.execute("""
        SELECT a.id, a.type, a.domaine, a.sous_domaine, a.libelle, c.code as cycle_code
        FROM attendu_scolaire a
        JOIN cycle c ON c.id = a.cycle_id
        WHERE a.cycle_id = ?
        ORDER BY a.type, a.domaine, a.id
    """, (cycle_id,)).fetchall()
    return [dict(r) for r in rows]


def supprimer_parents_redondants(conn, ids, table):
    if len(ids) <= 1:
        return ids
    rows = conn.execute(f"SELECT id, parent_id FROM {table}").fetchall()
    parent_of = {r[0]: r[1] for r in rows}

    def ancetres(nid):
        result = set()
        p = parent_of.get(nid)
        while p is not None:
            result.add(p)
            p = parent_of.get(p)
        return result

    tous_ancetres = set()
    for nid in ids:
        tous_ancetres |= ancetres(nid)
    return [nid for nid in ids if nid not in tous_ancetres]


def enregistrer_etape_a(conn, activite_id, resultats):
    """Enregistre description, meteo, thematiques, objectifs."""
    conn.execute("""
        UPDATE activite SET
            description    = ?,
            objectif_texte = ?,
            format_groupe  = ?,
            duree_min      = ?,
            meteo_soleil   = ?,
            meteo_pluie    = ?,
            meteo_vent     = ?,
            meteo_nuage    = ?,
            meteo_nuit     = ?
        WHERE id = ?
    """, (
        resultats.get("description"),
        resultats.get("objectif_texte"),
        resultats.get("format_groupe"),
        resultats.get("duree_min"),
        1 if resultats.get("meteo_soleil") else 0,
        1 if resultats.get("meteo_pluie")  else 0,
        1 if resultats.get("meteo_vent")   else 0,
        1 if resultats.get("meteo_nuage")  else 0,
        1 if resultats.get("meteo_nuit")   else 0,
        activite_id,
    ))

    them_ids = supprimer_parents_redondants(
        conn, resultats.get("thematique_ids", []), "thematique"
    )
    obj_ids = supprimer_parents_redondants(
        conn, resultats.get("objectif_ids", []), "objectif"
    )
    _inserer_relations(conn, activite_id, "activite_thematique", "thematique_id", them_ids)
    _inserer_relations(conn, activite_id, "activite_objectif",   "objectif_id",   obj_ids)

    # Mois
    mois_champs = ["jan","fev","mar","avr","mai","jun","jul","aou","sep","oct","nov","dec"]
    mois_data = resultats.get("mois", {})
    if mois_data:
        set_parts = ", ".join(f"mois_{m} = ?" for m in mois_champs)
        vals = [1 if mois_data.get(m) else 0 for m in mois_champs]
        conn.execute(
            f"UPDATE activite SET {set_parts} WHERE id = ?",
            vals + [activite_id]
        )

    conn.commit()


def enregistrer_etape_b(conn, activite_id, cycle_id, attendu_ids, ids_valides, statut="ok"):
    """Enregistre les attendus pour un cycle donne."""
    if statut == "ok":
        attendu_ids = [aid for aid in attendu_ids if aid in ids_valides]
        _inserer_relations(conn, activite_id, "activite_attendu", "attendu_id", attendu_ids)

        if attendu_ids:
            placeholders = ",".join("?" * len(attendu_ids))
            cycle_ids = [r[0] for r in conn.execute(
                f"SELECT DISTINCT cycle_id FROM attendu_scolaire WHERE id IN ({placeholders})",
                attendu_ids
            ).fetchall()]
            _inserer_relations(conn, activite_id, "activite_cycle", "cycle_id", cycle_ids)

    conn.execute(
        "INSERT OR REPLACE INTO activite_cycle_analysee (activite_id, cycle_id, statut) VALUES (?, ?, ?)",
        (activite_id, cycle_id, statut)
    )
    conn.commit()


def _inserer_relations(conn, activite_id, table, fk_col, ids):
    for fk_id in ids:
        try:
            conn.execute(
                f"INSERT OR IGNORE INTO {table} (activite_id, {fk_col}) VALUES (?, ?)",
                (activite_id, fk_id)
            )
        except Exception as e:
            print(f"    ATTENTION : {table} id={fk_id} : {e}")

# =============================================================================
# LECTURE FICHIERS _DESC_
# =============================================================================

def trouver_fichiers_desc(dossier: Path):
    if not dossier.exists():
        return []
    return [
        f for f in dossier.iterdir()
        if f.is_file()
        and f.name.startswith("_DESC_")
        and f.suffix.lower() in EXTENSIONS_SUPPORTEES
    ]


def fichier_vers_contenu(fichier: Path):
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
        return {"type": "text", "text": f"[Contenu de {fichier.name}]\n{texte}"}

    if ext == ".txt":
        try:
            texte = fichier.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            texte = f"[Erreur lecture TXT : {e}]"
        return {"type": "text", "text": f"[Contenu de {fichier.name}]\n{texte}"}

    return None

# =============================================================================
# APPEL API
# =============================================================================

SYSTEM_PROMPT_A = """Tu es un assistant specialise en pedagogie de la nature et en education a l'environnement.
Tu analyses des fiches d'activites pedagogiques nature et tu extrais des informations structurees.
Tu reponds UNIQUEMENT en JSON valide, sans aucun texte autour, sans balises markdown.
"""

SYSTEM_PROMPT_B = """Tu es un assistant specialise en pedagogie de la nature et en education a l'environnement.
Tu analyses des fiches d'activites pedagogiques nature pour identifier les attendus scolaires qu'elles travaillent.
Tu reponds toujours en deux blocs : d'abord un raisonnement en texte libre, puis un bloc JSON valide entre balises ```json.
"""


def appel_api(content, system_prompt, client):
    """Appel generique avec retry. Retourne le texte brut de la reponse."""
    MAX_RETRIES = 5
    for tentative in range(MAX_RETRIES):
        try:
            if API_PROVIDER == "gemini":
                import google.generativeai as genai
                model = genai.GenerativeModel(
                    model_name=GEMINI_MODEL,
                    system_instruction=system_prompt
                )
                parts = []
                for bloc in content:
                    if bloc["type"] == "text":
                        parts.append(bloc["text"])
                    elif bloc["type"] == "image":
                        parts.append({"inline_data": {
                            "mime_type": bloc["source"]["media_type"],
                            "data": bloc["source"]["data"]
                        }})
                    elif bloc["type"] == "document":
                        parts.append({"inline_data": {
                            "mime_type": "application/pdf",
                            "data": bloc["source"]["data"]
                        }})
                response = model.generate_content(parts)
                return response.text.strip()

            else:  # claude
                import anthropic
                response = client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=1500,
                    system=system_prompt,
                    messages=[{"role": "user", "content": content}]
                )
                return response.content[0].text.strip()

        except Exception as e:
            msg = str(e)
            is_prohibited = "PROHIBITED_CONTENT" in msg or "prohibited" in msg.lower()
            is_rate = "rate_limit" in msg or "429" in msg or "quota" in msg.lower() or "Resource" in msg

            if is_prohibited:
                raise RuntimeError("PROHIBITED_CONTENT")
            if is_rate:
                attente = 60 * (tentative + 1)
                print(f"  Rate limit. Attente {attente}s (tentative {tentative+1}/{MAX_RETRIES})...")
                time.sleep(attente)
                if tentative == MAX_RETRIES - 1:
                    raise
            else:
                raise

# =============================================================================
# ETAPE A — description, meteo, thematiques, objectifs, mois
# =============================================================================

def construire_prompt_a(nom, referentiels):
    def fmt(items, champs):
        lignes = []
        for item in items:
            parts = [f"id={item['id']}"]
            for c in champs:
                if c in item and item[c] is not None:
                    parts.append(f"{c}={item[c]}")
            lignes.append("  " + ", ".join(parts))
        return "\n".join(lignes)

    return f"""Tu vas analyser la fiche descriptive de l'activite pedagogique nature intitulee : << {nom} >>.

=== REFERENTIELS DISPONIBLES ===

THEMATIQUES (arbre hierarchique, niveau 0 = racine) :
{fmt(referentiels['thematiques'], ['nom', 'niveau'])}

OBJECTIFS (arbre hierarchique) :
{fmt(referentiels['objectifs'], ['nom', 'niveau'])}

=== INSTRUCTIONS ===

Retourne un JSON avec exactement ces champs :

{{
  "description": "Resume concis de l'activite en 2-4 phrases. En francais.",
  "objectif_texte": "Objectif pedagogique principal en 1-2 phrases. En francais.",
  "format_groupe": "Une valeur parmi : individuel / binome / petit groupe / grand groupe. Null si non determinable.",
  "duree_min": entier ou null,
  "meteo_soleil": true/false — true UNIQUEMENT si l'activite necessite absolument le soleil,
  "meteo_pluie": true/false — true UNIQUEMENT si l'activite necessite absolument la pluie,
  "meteo_vent": true/false — true UNIQUEMENT si l'activite necessite absolument le vent,
  "meteo_nuage": true/false — true UNIQUEMENT si l'activite necessite absolument un ciel nuageux,
  "meteo_nuit": true/false — true UNIQUEMENT si l'activite se deroule obligatoirement de nuit,
  "mois": {{
    "jan": true/false, "fev": true/false, "mar": true/false, "avr": true/false,
    "mai": true/false, "jun": true/false, "jul": true/false, "aou": true/false,
    "sep": true/false, "oct": true/false, "nov": true/false, "dec": true/false
  }},
  "thematique_ids": [liste des id — choisis les plus precis, max 5],
  "objectif_ids": [liste des id — choisis les plus precis, max 3]
}}

REGLES :
- Ne propose que des IDs qui existent dans les referentiels fournis.
- Pour les thematiques et objectifs : choisis les noeuds les plus precis. Ne selectionne JAMAIS un noeud parent ET l'un de ses descendants.
- Pour la meteo : true SEULEMENT si l'activite est IMPOSSIBLE ou perd son sens sans cette condition.
- Pour les mois : true si l'activite est pertinente ce mois-la (selon les elements naturels utilises, la saison, etc.).
- Le JSON doit etre valide et complet. Aucun texte en dehors du JSON.
"""


def analyser_etape_a(nom, fichiers, referentiels, client):
    content = [{"type": "text", "text": construire_prompt_a(nom, referentiels)}]
    for f in fichiers:
        bloc = fichier_vers_contenu(f)
        if bloc:
            content.append({"type": "text", "text": f"\n--- Fichier : {f.name} ---"})
            content.append(bloc)

    raw = appel_api(content, SYSTEM_PROMPT_A, client)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        if "```" in raw:
            partie = raw.split("```")[1]
            if partie.startswith("json"):
                partie = partie[4:]
            return json.loads(partie.strip())
        raise

# =============================================================================
# ETAPE B — attendus scolaires par cycle
# =============================================================================

def construire_prompt_b(nom, cycle_num, referentiel):
    labels = {1: "3-6 ans (maternelle / Cycle 1)",
              2: "6-9 ans (CP, CE1, CE2 / Cycle 2)",
              3: "9-12 ans (CM1, CM2, 6e / Cycle 3)"}
    label = labels.get(cycle_num, f"Cycle {cycle_num}")

    def fmt_attendu(a):
        sd = f" / {a['sous_domaine']}" if a['sous_domaine'] else ""
        return f"  id={a['id']}, type={a['type']}, domaine={a['domaine']}{sd}, libelle={a['libelle']}"

    ref_text = "\n".join(fmt_attendu(a) for a in referentiel)

    return f"""Tu vas identifier les attendus scolaires travailles par l'activite pedagogique nature intitulee : << {nom} >>.

Tu dois d'abord juger si cette activite est adaptee au Cycle {cycle_num} ({label}).
Si elle n'est pas adaptee a ce cycle, retourne {{"attendu_ids": [], "_inadapte": true}}.
Sinon, selectionne les attendus pertinents parmi ceux disponibles.

=== ATTENDUS SCOLAIRES DISPONIBLES (Cycle {cycle_num}) ===
{ref_text}

=== INSTRUCTIONS ===

RAISONNEMENT (texte libre, 2-3 phrases) :
Indique si l'activite est adaptee au cycle. Si oui, justifie les attendus retenus.

JSON :
```json
{{"attendu_ids": [liste des id ou tableau vide], "_inadapte": true/false}}
```

REGLES :
- Ne propose que des IDs qui existent dans le referentiel fourni.
- Sois TRES selectif : ne retiens que les attendus qui correspondent DIRECTEMENT et PRECISEMENT a ce que l'activite fait concretement.
- Un attendu ne doit etre retenu que si un animateur pourrait affirmer sans hesitation que l'activite le travaille vraiment.
- Si l'activite est simple et ciblee, 1 ou 2 attendus suffisent.
- Maximum 10 attendus au total. En cas de doute, ne pas retenir.
- Si aucun attendu ne correspond clairement, retourne {{"attendu_ids": [], "_inadapte": false}}.
"""


def parser_reponse_b(raw):
    """Parse la reponse etape B (raisonnement + JSON). Retourne (data_dict, raisonnement)."""
    raisonnement = ""
    data = None

    if "```json" in raw:
        parties = raw.split("```json")
        raisonnement = parties[0].strip()
        json_str = parties[1].split("```")[0].strip()
        try:
            data = json.loads(json_str)
        except Exception:
            data = {"attendu_ids": [], "_statut": "erreur_parsing"}
    elif "```" in raw:
        parties = raw.split("```")
        raisonnement = parties[0].strip()
        partie = parties[1]
        if partie.startswith("json"):
            partie = partie[4:]
        try:
            data = json.loads(partie.strip())
        except Exception:
            data = {"attendu_ids": [], "_statut": "erreur_parsing"}
    else:
        try:
            data = json.loads(raw.strip())
        except Exception:
            idx = raw.find('{"attendu_ids"')
            if idx == -1:
                idx = raw.find('{ "attendu_ids"')
            if idx != -1:
                raisonnement = raw[:idx].strip()
                try:
                    data = json.loads(raw[idx:].strip())
                except Exception:
                    data = {"attendu_ids": [], "_statut": "erreur_parsing"}
            else:
                data = {"attendu_ids": [], "_statut": "erreur_parsing"}
                raisonnement = raw.strip()

    if not isinstance(data, dict):
        data = {"attendu_ids": [], "_statut": "erreur_parsing"}

    return data, raisonnement


def analyser_etape_b(nom, fichiers, cycle_num, referentiel, client):
    content = [{"type": "text", "text": construire_prompt_b(nom, cycle_num, referentiel)}]
    for f in fichiers:
        bloc = fichier_vers_contenu(f)
        if bloc:
            content.append({"type": "text", "text": f"\n--- Fichier : {f.name} ---"})
            content.append(bloc)

    try:
        raw = appel_api(content, SYSTEM_PROMPT_B, client)
    except RuntimeError as e:
        if "PROHIBITED_CONTENT" in str(e):
            return {"attendu_ids": [], "_statut": "prohibited"}, ""
        raise

    data, raisonnement = parser_reponse_b(raw)
    return data, raisonnement

# =============================================================================
# SCAN DES NOUVEAUX DOSSIERS
# =============================================================================

def scanner_nouveaux_dossiers(conn):
    """Retourne les (dossier, fichiers_desc) pour les activites absentes de la BDD."""
    noms_bdd = noms_activites_en_bdd(conn)
    nouveaux = []

    for dossier in sorted(DROPBOX_ACTIVITES.iterdir()):
        # Ignorer les fichiers et les dossiers de groupes (prefixe _)
        if not dossier.is_dir():
            continue
        if any(dossier.name.startswith(p) for p in PREFIXES_IGNORES):
            continue

        nom = dossier.name
        if nom in noms_bdd:
            continue

        fichiers = trouver_fichiers_desc(dossier)
        if not fichiers:
            continue  # ignorer silencieusement

        nouveaux.append((nom, dossier, fichiers))

    return nouveaux

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("INTEGRATION DES NOUVELLES ACTIVITES")
    print(f"API : {API_PROVIDER.upper()} ({GEMINI_MODEL if API_PROVIDER == 'gemini' else CLAUDE_MODEL})")
    print("=" * 60)

    if not DB_PATH.exists():
        print(f"ERREUR : Base SQLite introuvable : {DB_PATH}")
        sys.exit(1)

    if not DROPBOX_ACTIVITES.exists():
        print(f"ERREUR : Repertoire introuvable : {DROPBOX_ACTIVITES}")
        sys.exit(1)

    # Initialiser le client API
    if API_PROVIDER == "gemini":
        import google.generativeai as genai
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_key:
            print("ERREUR : variable GEMINI_API_KEY non definie.")
            sys.exit(1)
        genai.configure(api_key=gemini_key)
        client = genai
    else:
        import anthropic
        client = anthropic.Anthropic()

    conn = get_db()

    # Verifier que les tables necessaires existent
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    for t in ["activite_cycle_analysee", "attendu_scolaire", "cycle"]:
        if t not in tables:
            print(f"ERREUR : table '{t}' absente. Verifiez que les migrations ont ete lancees.")
            conn.close()
            sys.exit(1)

    # Charger les referentiels communs
    print("\nChargement des referentiels...")
    referentiels = charger_referentiels(conn)
    cycles = referentiels["cycles"]
    print(f"  {len(referentiels['thematiques'])} thematiques, {len(referentiels['objectifs'])} objectifs, {len(cycles)} cycles")

    # Charger les attendus par cycle
    attendus_par_cycle = {}
    ids_valides_par_cycle = {}
    for cy in cycles:
        attendus = charger_attendus_cycle(conn, cy["id"])
        attendus_par_cycle[cy["id"]] = (cy, attendus)
        ids_valides_par_cycle[cy["id"]] = {a["id"] for a in attendus}
        print(f"  C{cy['code']} : {len(attendus)} attendus")

    # Scanner les nouveaux dossiers
    print("\nScan des nouveaux dossiers...")
    nouveaux = scanner_nouveaux_dossiers(conn)
    print(f"  {len(nouveaux)} nouveau(x) dossier(s) avec fichier(s) _DESC_")

    if not nouveaux:
        print("\nOK Rien a faire.")
        conn.close()
        return

    if LIMITE:
        nouveaux = nouveaux[:LIMITE]
        print(f"  Mode test : limite de {LIMITE}")

    # Initialiser le log
    log_path = Path(__file__).parent / "integration_raisonnements.log"
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"=== INTEGRATION — {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    print(f"\n{'=' * 60}")
    print(f"Traitement de {len(nouveaux)} activite(s)...")
    print(f"{'=' * 60}\n")

    succes = 0
    erreurs = 0

    for i, (nom, dossier, fichiers) in enumerate(nouveaux, 1):
        print(f"[{i}/{len(nouveaux)}] {nom}")
        print(f"   Fichiers : {', '.join(f.name for f in fichiers)}")

        try:
            # --- Insertion en BDD ---
            activite_id = inserer_activite(conn, nom, dossier)
            print(f"   Inseree en BDD (id={activite_id})")

            # --- Etape A : description, meteo, thematiques, objectifs, mois ---
            print("   Etape A : description / meteo / thematiques / mois...")
            time.sleep(DELAI_ENTRE_APPELS)
            resultats_a = analyser_etape_a(nom, fichiers, referentiels, client)
            enregistrer_etape_a(conn, activite_id, resultats_a)
            nb_them = len(resultats_a.get("thematique_ids", []))
            nb_mois = sum(1 for v in resultats_a.get("mois", {}).values() if v)
            print(f"   OK : {nb_them} thematique(s), {nb_mois} mois")

            # --- Etape B : attendus par cycle ---
            for cy_id, (cy, referentiel) in attendus_par_cycle.items():
                cycle_num = int(cy["code"].replace("C", ""))
                print(f"   Etape B {cy['code']} : attendus...")
                time.sleep(DELAI_ENTRE_APPELS)

                data, raisonnement = analyser_etape_b(nom, fichiers, cycle_num, referentiel, client)

                # Ecrire le raisonnement dans le log
                if raisonnement:
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(f"\n=== {nom} — {cy['code']} ===\n{raisonnement}\n")

                attendu_ids = data.get("attendu_ids", [])
                if not isinstance(attendu_ids, list):
                    attendu_ids = []
                attendu_ids = [int(aid) for aid in attendu_ids
                               if str(aid).isdigit() or isinstance(aid, int)]

                # Determiner le statut
                statut_raw = data.get("_statut", "ok")
                inadapte = data.get("_inadapte", False)

                if statut_raw == "prohibited":
                    statut = "prohibited"
                elif statut_raw == "erreur_parsing":
                    statut = "erreur_parsing"
                elif inadapte:
                    statut = "inadapte"
                else:
                    statut = "ok"

                enregistrer_etape_b(conn, activite_id, cy_id, attendu_ids, ids_valides_par_cycle[cy_id], statut)
                print(f"      {cy['code']} : {statut} ({len(attendu_ids)} attendu(s))")

            succes += 1

        except Exception as e:
            print(f"   ERREUR : {e}")
            erreurs += 1

        print()

    conn.close()

    print("=" * 60)
    print(f"Termine : {succes} succes, {erreurs} erreur(s)")
    print(f"Log des raisonnements : {log_path.name}")
    print("=" * 60)


if __name__ == "__main__":
    main()
