# BDD Activités — Documentation

Application web locale pour naviguer, rechercher et planifier des activités pédagogiques nature.

---

## Contexte

Bibliothèque de ~1426 activités stockées dans :
```
C:\Users\moina\Dropbox\Animation\Activités v2\
```
Chaque sous-dossier est une activité. Les fichiers descriptifs sont préfixés `_DESC_` (`.pdf`, `.docx`, `.txt`, `.jpg`, `.png`).

Suivi dans : `Activités v2 ajouts.xlsx`

---

## Architecture

```
_OUTIL/
├── main.py                      # Backend FastAPI + endpoints API
├── activites.db                 # Base SQLite (générée, non versionnée)
├── config.json                  # Chemin vers l'Excel (non versionné)
├── static/
│   └── index.html               # Frontend HTML/JS pur
│
├── create_schema.py             # Étape 1 — crée le schéma SQLite
├── migrate_excel.py             # Étape 2 — importe les activités depuis l'Excel
├── import_classification.py     # Étape 3 — thématiques et objectifs
├── import_pedagogies.py         # Étape 4 — pédagogies, théories, cycles
├── import_attendus.py           # Étape 5 — attendus scolaires EDD
├── migration_ajout_cycle.py     # Étape 6 — ajoute la table activite_cycle
├── analyser_activites.py        # Étape 7 — analyse IA des fichiers _DESC_
│
├── export_activites.py          # Outil : export Excel pour analyse des tags
│
├── reinitialiser_bdd.bat        # Lance les étapes 1 à 6 en séquence
├── demarrer_app.bat             # Lance le serveur FastAPI
└── *.bat                        # Un .bat par script Python
```

**Stack :**
- Backend : FastAPI + SQLite
- Frontend : HTML/JS pur (aucune dépendance externe)
- IA : Google Gemini 2.5 Flash (analyse des fiches) — Anthropic Claude en option

---

## Prérequis

### Python
```
pip install fastapi uvicorn openpyxl pandas google-generativeai python-docx pillow
```

### Variables d'environnement Windows
```
setx GEMINI_API_KEY "votre-clé-gemini"
setx ANTHROPIC_API_KEY "votre-clé-claude"   # optionnel
```

### config.json
Fichier à créer manuellement dans le dossier `_OUTIL\` :
```json
{
  "excel_output": "C:\\Users\\moina\\Dropbox\\Animation\\Activités v2\\Activités v2 ajouts.xlsx"
}
```

---

## Mise en place — première installation

Lancer dans l'ordre, ou via `reinitialiser_bdd.bat` (étapes 1 à 6) :

### Étape 1 — Créer le schéma
```
create_schema.bat
```
Crée `activites.db` avec toutes les tables. Idempotent (peut être relancé sans détruire les données).

**Tables créées :**
- `activite` — table principale (nom, lieu, météo, mois, description, etc.)
- `thematique`, `objectif` — hiérarchies auto-référentielles
- `pedagogie`, `theorie_apprentissage`, `cycle`, `attendu_scolaire`, `competence`, `tag`
- Tables de liaison : `activite_thematique`, `activite_objectif`, `activite_attendu`, `activite_cycle`, `activite_tag`, etc.
- Tables de planification : `sejour`, `sequence`, `sequence_activite`

### Étape 2 — Importer les activités depuis l'Excel
```
migrate_excel.bat
```
Importe depuis `Activités v2 ajouts.xlsx` :
- Nom de l'activité, chemin du dossier, si animée ou non
- Lieu (Intérieur / Extérieur / Intérieur/Extérieur)
- Mois de pratique (colonnes J→D)

⚠️ La **météo n'est pas importée** depuis l'Excel — elle sera déterminée par l'analyse IA.
⚠️ Utilise `INSERT OR IGNORE` : relancer n'écrase pas les données existantes.

> En cas d'erreur, utiliser `debug_migrate.bat` qui redirige la sortie vers `migration_log.txt`.

### Étape 3 — Importer la classification
```
import_classification.bat
```
Importe en base :
- **298 thématiques** organisées en arbre hiérarchique (Biosphère, Lithosphère, Atmosphère, Biologie, Astronomie, etc.)
- **19 objectifs** en arbre (Connexion à la nature, Connaître, Agir, Se mouvoir, Créer)

Données hardcodées dans `import_classification.py`. Idempotent.

### Étape 4 — Importer les pédagogies
```
import_pedagogies.bat
```
Importe en base :
- **19 pédagogies** (apprentissage expérientiel, pédagogie de l'imaginaire, classe inversée, etc.)
- **9 théories d'apprentissage** (Vygotsky, Piaget, Bruner, etc.)
- **4 cycles scolaires** (C1 maternelle, C2 CP-CE2, C3 CM1-6e, C4 5e-3e)

Données hardcodées avec résumés et liens Notion. Idempotent.

### Étape 5 — Importer les attendus scolaires
```
import_attendus.bat
```
Importe **72 attendus EDD** (Éducation au Développement Durable) en base, répartis sur 4 cycles × 6 thèmes × 3 sous-thèmes. Source : `Attendus_scolaires.txt`. Idempotent.

### Étape 6 — Migration table cycles
```
migration_ajout_cycle.bat
```
Crée la table `activite_cycle` si elle est absente (`CREATE TABLE IF NOT EXISTS`). Nécessaire sur une base existante avant l'analyse IA.

### Étape 7 — Analyser les activités avec l'IA
```
analyser_activites.bat
```
Pour chaque dossier d'activité avec un fichier `_DESC_`, envoie le contenu à l'API Gemini (ou Claude) et enregistre en base :
- `description`, `objectif_texte`, `format_groupe`, `duree_min`
- Météo requise : `meteo_soleil`, `meteo_pluie`, `meteo_vent`, `meteo_nuage`, `meteo_nuit`
- `thematique_ids`, `objectif_ids`, `attendu_ids`
- `cycle_ids` — dérivés automatiquement depuis les attendus sélectionnés

**Variables de configuration** (en haut de `analyser_activites.py`) :
```python
API_PROVIDER = "gemini"       # "gemini" ou "claude"
GEMINI_MODEL = "gemini-2.5-flash"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
LIMITE = None                 # None = tout analyser | entier = mode test
FORCER_REANALYSE = False      # True = retraiter les activités déjà analysées
ANALYSER_PEDAGOGIES = False   # désactivé (réduit la taille du prompt)
ANALYSER_THEORIES = False     # désactivé
DELAI_ENTRE_APPELS = 15       # secondes entre deux appels API
```

**Comportement :**
- Activités sans fichier `_DESC_` ignorées (~125 activités)
- Retry automatique sur rate limit (jusqu'à 5 tentatives, délai croissant)
- Post-traitement : suppression automatique des thématiques parents redondants
- Cycles dérivés depuis les attendus, pas assignés directement par l'IA

**Formats supportés pour `_DESC_` :** `.pdf`, `.docx`, `.txt`, `.jpg`, `.jpeg`, `.png`

---

## Réinitialisation complète
```
reinitialiser_bdd.bat
```
Supprime `activites.db`, puis relance les étapes 1 à 6 dans l'ordre.
⚠️ Ne relance **pas** l'étape 7 (analyse IA) — à lancer séparément.

---

## Lancer l'application
```
demarrer_app.bat
```
- Vérifie la présence de `activites.db`
- Installe FastAPI/uvicorn si absent
- Ouvre `http://localhost:8000` dans le navigateur
- Lance uvicorn en mode `--reload`

---

## API — Endpoints disponibles

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/activites` | Liste avec filtres combinés |
| GET | `/api/activites/{id}` | Détail complet avec toutes les relations |
| PUT | `/api/activites/{id}` | Modifier une activité |
| GET | `/api/activites/{id}/ouvrir-dossier` | Ouvre le dossier dans l'explorateur Windows |
| GET | `/api/thematiques` | Liste par niveau |
| GET | `/api/thematiques/arbre` | Arbre complet imbriqué |
| GET | `/api/objectifs` | Liste par niveau |
| GET | `/api/objectifs/arbre` | Arbre complet imbriqué |
| GET | `/api/cycles` | Liste des cycles |
| GET | `/api/cycles/{id}/attendus` | Attendus d'un cycle |
| GET | `/api/tags` | Liste des tags |
| POST | `/api/tags` | Créer un tag |
| PUT | `/api/tags/{id}` | Renommer un tag |
| DELETE | `/api/tags/{id}` | Supprimer un tag |
| GET | `/api/stats` | Statistiques générales |

**Paramètres de filtre sur `/api/activites` :**

| Paramètre | Valeurs possibles |
|-----------|-------------------|
| `q` | texte libre (nom, description, objectif) |
| `lieu` | Intérieur / Extérieur / Intérieur/Extérieur |
| `meteo` | nuage / soleil / pluie / vent / nuit |
| `mois` | jan / fev / mar / avr / mai / jun / jul / aou / sep / oct / nov / dec |
| `competence` | individuel / binôme / petit groupe / grand groupe |
| `thematique_id` | ID — inclut récursivement les sous-thématiques |
| `objectif_id` | ID — inclut récursivement les sous-objectifs |
| `cycle_ids` | IDs séparés par virgules |
| `attendu_ids` | IDs séparés par virgules |
| `tag_ids` | IDs séparés par virgules |
| `limit` / `offset` | pagination (max 200) |

---

## Fonctionnalités de l'interface

- Recherche full-text + filtres combinés dans la sidebar
- Sélection thématique/objectif via arbre modal avec recherche et déplier/replier
- Filtre mois par boutons toggle
- Filtre cycles + attendus en cascade (sélectionner un cycle affiche ses attendus)
- Filtre tags
- Fiche détail : météo, mois, description, visée pédagogique, thématiques, objectifs, attendus groupés par cycle, tags, bouton "ouvrir le dossier"
- Mode édition complet depuis la fiche (tous les champs + relations)
- Création de tags depuis le mode édition
- Pagination (40 résultats par page)

---

## Outils complémentaires

### export_activites.py / export_activites.bat
Exporte toutes les activités (nom + description + thématiques) vers `export_tags.xlsx`, avec une colonne vide "Tags suggérés" pour annotation manuelle. Utilité : analyser les données pour identifier des regroupements pertinents par tags.

---

## Conventions

- Préfixe `_` sur les **dossiers contenants** (groupes), pas sur les dossiers d'activités
- `chemin_dossier` en base = chemin Windows complet vers le dossier de l'activité
- `activites.db` et `config.json` sont dans `.gitignore`

---

## État du projet

- [x] Schéma BDD créé
- [x] 1426 activités importées depuis l'Excel
- [x] Classification (298 thématiques, 19 objectifs), pédagogies, attendus importés
- [x] Analyse IA terminée — 1301 activités traitées (125 sans _DESC_ ignorées)
- [x] Interface web complète (filtres, fiche détail, mode édition, tags)
- [ ] Création des tags (à faire dans l'interface web)
- [ ] Traitement des 125 activités sans fichier _DESC_
- [ ] Planification de séjours (structure BDD prête, interface à développer)
