# =============================================================================
# doc2.py
# =============================================================================
# « Déroulé et objectifs » (ex Doc 2) d'un dossier de séjour :
# « Séjour_JJ-MM_Nom_Déroulé&Objectifs-pédagogiques.docx ».
#
#   - remplir_doc2 : écrit les infos du séjour (Projets enseignants), les matinées (roulement),
#                    les activités choisies, l'activité « si pluie » et les ressources en autonomie.
#
# Règle de sécurité : une case n'est modifiée que si elle est vide, ou si elle contient encore
# exactement ce que l'outil y avait écrit la dernière fois. Un texte que tu as retouché est conservé.
# =============================================================================

import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import doc3 as D

JOURS_SEMAINE = ["Mardi", "Mercredi", "Jeudi", "Vendredi"]
JOURS_ACTIVITES = ["lundi", "mardi", "mercredi", "jeudi"]
VIDES = {"", "…", "...", "jj/mm/aaaa"}


def trouver_doc2(dossier: Path) -> Optional[Path]:
    for f in sorted(dossier.glob("Séjour_*Déroulé*.docx")):
        if not f.name.startswith("~$"):
            return f
    return None


def assurer_doc2(dossier: Path, s: dict) -> Path:
    """Retourne le document du dossier ; le copie depuis le modèle B s'il manque."""
    f = trouver_doc2(dossier)
    if f:
        return f
    modele = next(iter(sorted((D.dossier_annee() / D.NOM_MODELE_B).glob("Séjour_*Déroulé*.docx"))), None)
    if modele is None:
        raise FileNotFoundError(f"« déroulé et objectifs » introuvable dans le modèle B ({D.NOM_MODELE_B})")
    jj_mm = f"{s['date_debut'][8:10]}-{s['date_debut'][5:7]}"
    nom = modele.name.replace("00-00", jj_mm, 1).replace("_Nom_", f"_{D.nom_court(s.get('enseignant'))}_", 1)
    cible = dossier / nom
    shutil.copy2(modele, cible)
    return cible


def _fr(iso: str) -> str:
    return f"{iso[8:10]}/{iso[5:7]}/{iso[:4]}"


def _matins(texte: Optional[str]) -> Dict[str, str]:
    out = {}
    for l in (texte or "").splitlines():
        m = re.match(r"\s*(\w+)\s*:\s*(.+?)\s*$", l)
        if m:
            out[m.group(1).capitalize()] = m.group(2)
    return out


def _ecrire(cell, texte: str):
    """Écrit dans la cellule en gardant la mise en forme du premier morceau de texte."""
    p = cell.paragraphs[0]
    if p.runs:
        p.runs[0].text = texte
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(texte)


def _style_comme(cible, modele):
    """Applique à la cellule le style de texte d'une cellule déjà rédigée (plus de gris italique du modèle)."""
    import copy
    ref = modele.paragraphs[0].runs[0] if modele.paragraphs[0].runs else None
    run = cible.paragraphs[0].runs[0] if cible.paragraphs[0].runs else None
    if ref is None or run is None:
        return
    ancien = run._r.rPr
    if ancien is not None:
        run._r.remove(ancien)
    if ref._r.rPr is not None:
        run._r.insert(0, copy.deepcopy(ref._r.rPr))


def _cellules_distinctes(row) -> list:
    vues, out = [], []
    for c in row.cells:
        if c._tc not in vues:
            vues.append(c._tc)
            out.append(c)
    return out


COULEUR_TITRE = "1F3864"  # bleu des libellés du document


def _blocs_detail(acts: List[dict], champ: str, prefixe: str = "") -> List[tuple]:
    """[(titre, texte)] d'un créneau. Une activité seule : son texte sans titre (son nom figure déjà
    dans le tableau de l'emploi du temps) ; plusieurs : un bloc par activité, titré de son nom."""
    if not any(a.get(champ) for a in acts):
        return []
    if len(acts) == 1 and not prefixe:
        return [(None, acts[0][champ])]
    # plusieurs activités : on les liste toutes, pour que « objectifs » et « descriptif » restent alignés
    return [(f"{prefixe}{a['nom']}", a.get(champ) or "—") for a in acts]


def _texte_blocs(blocs: List[tuple]) -> str:
    """Texte à plat des blocs (un paragraphe par ligne) : sert à repérer si tu as retouché la case."""
    lignes = []
    for titre, texte in blocs:
        if titre:
            lignes.append(titre)
        lignes.append(texte)
    return "\n".join(lignes)


def _ecrire_blocs(cell, blocs: List[tuple]):
    """Un paragraphe pour le titre de chaque activité (gras, bleu, espacé de la précédente), puis un
    paragraphe pour son texte. La pagination de la case (maintien avec la ligne suivante) est conservée."""
    import copy
    from docx.shared import Pt, RGBColor
    p0 = cell.paragraphs[0]
    for p in cell.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    for r in list(p0.runs):
        r._r.getparent().remove(r._r)
    lignes = []
    for k, (titre, texte) in enumerate(blocs):
        if titre:
            lignes.append((titre, True, k > 0))
        lignes.append((texte, False, False))
    ppr = p0._p.pPr
    for i, (texte, est_titre, espace) in enumerate(lignes):
        if i == 0:
            p = p0
        else:
            p = cell.add_paragraph()
            if ppr is not None:
                p._p.insert(0, copy.deepcopy(ppr))
        run = p.add_run(texte)
        if est_titre:
            run.bold = True
            run.font.color.rgb = RGBColor.from_string(COULEUR_TITRE)
        if espace:
            p.paragraph_format.space_before = Pt(8)


LIBELLE_PLUIE = "Si pluie"
MENTION_PLUIE = "uniquement par temps de pluie, à la place de l'activité d'une des après-midis"


def _est_pluie(texte: str) -> bool:
    return D.norm(texte).startswith("sipluie")


def _vider(cell):
    """Vide une cellule en gardant la mise en forme de son premier paragraphe."""
    for p in cell.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    _ecrire_paragraphe(cell.paragraphs[0], "")


def _ligne_pluie_edt(edt, entetes: List[str]):
    """Ligne « Si pluie » de l'emploi du temps, ajoutée sous « Après-midi » si elle manque.
    Lundi → jeudi ne forment qu'une case : l'activité ne dépend pas du jour."""
    lignes = list(edt.rows[1:])
    for r in lignes:
        if _est_pluie(r.cells[0].text):
            return r
    apres = next((r for r in lignes if D.norm(r.cells[0].text) == "apresmidi"), None)
    modele = next((r for r in lignes if D.norm(r.cells[0].text) == "veillee"), apres)
    if apres is None or not all(j in entetes for j in JOURS_ACTIVITES):
        return None
    import copy
    tr = copy.deepcopy(modele._tr)
    apres._tr.addnext(tr)
    row = next(r for r in edt.rows if r._tr is tr)
    _ecrire(row.cells[0], LIBELLE_PLUIE)
    debut, fin = entetes.index(JOURS_ACTIVITES[0]), entetes.index(JOURS_ACTIVITES[-1])
    for i in range(debut, fin + 1):
        _vider(row.cells[i])
    row.cells[debut].merge(row.cells[fin])
    row = next(r for r in edt.rows if r._tr is tr)
    _vider(row.cells[debut])  # la fusion laisse un paragraphe vide par case regroupée
    _ecrire(row.cells[debut], "…")
    for i, jour in enumerate(entetes):
        if i and jour not in JOURS_ACTIVITES:
            _ecrire(row.cells[i], "—")
    return row


def _bloc_pluie_detail(table):
    """Ajoute au détail des activités un bloc « Si pluie / Après-midi » (objectifs, descriptif),
    copié du bloc du jeudi, s'il n'existe pas encore."""
    lignes = [(r, _cellules_distinctes(r)) for r in table.rows]
    if any(c and _est_pluie(c[0].text) for _, c in lignes):
        return
    jeudi = [r for r, c in lignes if len(c) >= 3 and D.norm(c[0].text).startswith("jeudi")]
    if not jeudi:
        return
    import copy
    ancre, nouveaux = jeudi[-1]._tr, []
    for r in jeudi:
        tr = copy.deepcopy(r._tr)
        ancre.addnext(tr)
        ancre = tr
        nouveaux.append(tr)
    for k, tr in enumerate(nouveaux):
        row = next(r for r in table.rows if r._tr is tr)
        cells = _cellules_distinctes(row)
        if k == 0:
            _ecrire_paragraphe(cells[0].paragraphs[0], LIBELLE_PLUIE)
        _vider(cells[2])


TITRE_RESSOURCES = "Ressources en autonomie"


def _details_ressource(r: dict) -> str:
    bouts = []
    if r.get("effectif_min") and r.get("effectif_max"):
        bouts.append(f"{r['effectif_min']} à {r['effectif_max']} joueurs" if r["effectif_min"] != r["effectif_max"]
                     else f"{r['effectif_min']} joueurs")
    elif r.get("effectif_min"):
        bouts.append(f"à partir de {r['effectif_min']} joueurs")
    if r.get("duree_min"):
        bouts.append(f"environ {r['duree_min']} min")
    if r.get("format_groupe"):
        bouts.append(r["format_groupe"])
    return " · ".join(bouts)


def _resume(texte: Optional[str], limite: int = 220) -> str:
    t = " ".join((texte or "").split())
    if len(t) <= limite:
        return t
    coupe = t[:limite]
    fin = max(coupe.rfind(". "), coupe.rfind(" "))
    return coupe[:fin if fin > 60 else limite].rstrip(" ,;:.") + "…"


def _texte_ressources(ressources: List[dict]) -> str:
    lignes = []
    for r in ressources:
        det = _details_ressource(r)
        ligne = r["nom"] + (f" ({det})" if det else "")
        if r.get("description"):
            ligne += " : " + _resume(r["description"])
        lignes.append(ligne)
    return "\n".join(lignes)


def _maj_ressources(doc, ressources: List[dict], ecrits: dict, nouveaux: dict, remplis: list, conserves: list):
    """Titre « Ressources en autonomie » puis un paragraphe géré par l'outil. Tu peux écrire à la suite.
    Le paragraphe n'est modifié que s'il est inchangé depuis la dernière écriture de l'outil."""
    import copy
    cle, valeur = "ressources", _texte_ressources(ressources)
    titre = next((p for p in doc.paragraphs if p.text.strip().lower() == TITRE_RESSOURCES.lower()), None)
    if titre is None:
        if not ressources:
            return  # rien à écrire : pas de rubrique vide
        modele = next((p for p in doc.paragraphs if p.text.strip().startswith("Emploi du temps de la semaine")), None)
        if modele is not None:  # même présentation que les autres titres du document
            doc.element.body.sectPr.addprevious(copy.deepcopy(modele._p))
            titre = doc.paragraphs[-1]
            _ecrire_paragraphe(titre, TITRE_RESSOURCES)
        else:
            titre = doc.add_paragraph()
            titre.add_run(TITRE_RESSOURCES).bold = True
        corps = doc.add_paragraph(valeur)
        nouveaux[cle] = valeur
        remplis.append("Ressources en autonomie")
        return
    suivant = titre._p.getnext()
    corps = next((p for p in doc.paragraphs if p._p is suivant), None)
    if corps is None:
        corps = doc.add_paragraph("")
        titre._p.addnext(corps._p)
    actuel, avant = corps.text.strip(), ecrits.get(cle)
    if actuel == valeur.strip():
        nouveaux[cle] = valeur
    elif actuel in VIDES or (avant is not None and actuel == avant.strip()):
        _ecrire_paragraphe(corps, valeur)
        nouveaux[cle] = valeur
        remplis.append("Ressources en autonomie")
    else:
        conserves.append("Ressources en autonomie")


def _ecrire_paragraphe(p, texte: str):
    if p.runs:
        p.runs[0].text = texte
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(texte)


def remplir_doc2(chemin: Path, s: dict, planning: Optional[dict] = None, ecrits: Optional[dict] = None) -> dict:
    """Met à jour le document. Retourne {'fichier', 'remplis', 'conserves', 'ecrits'} ;
    'ecrits' = ce que l'outil a écrit (à mémoriser pour la prochaine mise à jour)."""
    from docx import Document
    doc = Document(chemin)
    ecrits = dict(ecrits or {})
    nouveaux: Dict[str, str] = dict(ecrits)
    remplis: List[str] = []
    conserves: List[str] = []
    pluie = s.get("pluie")  # None : séjour sans plan pluie connu, on ne touche pas au document

    def poser(cell, valeur: Optional[str], cle: str, nom: str, style_de=None, ecrire=None):
        if valeur is None:
            return
        actuel = cell.text.strip()
        avant = ecrits.get(cle)
        if actuel == valeur.strip():
            nouveaux[cle] = valeur
            return
        if actuel in VIDES or (avant is not None and actuel == avant.strip()):
            if ecrire is not None:
                ecrire(cell)
            else:
                _ecrire(cell, valeur)
            if style_de is not None:
                _style_comme(cell, style_de)
            nouveaux[cle] = valeur
            remplis.append(nom)
        else:
            conserves.append(nom)

    # 1. « Séjour du jj/mm/aaaa au jj/mm/aaaa » (une seule fois : les dates ne changent pas)
    for p in doc.paragraphs:
        if p.text.strip().startswith("Séjour du"):
            dates = iter([_fr(s["date_debut"]), _fr(s["date_fin"])])
            fait = False
            for r in p.runs:
                if r.text.strip() == "jj/mm/aaaa":
                    r.text = next(dates)
                    r.italic = False
                    fait = True
            if fait:
                remplis.append("Dates du séjour")
            break

    # 2. Fiche du séjour (premier tableau)
    classe = " — ".join(x for x in (s.get("ecole"), s.get("niveau1")) if x)
    valeurs = {
        "thematique": s.get("thematique_excel"),
        "objectifsdusejour": s.get("objectifs_texte"),
        "ecoleclasse": classe or None,
        "enseignantreferent": s.get("enseignant"),
        "unite": (s.get("unite") or "").capitalize() or None,
    }
    for row in doc.tables[0].rows:
        cells = _cellules_distinctes(row)
        libelle = D.norm(cells[0].text)
        if libelle == "mediateurreferent":
            if len(cells) >= 5:
                poser(cells[2], s.get("mediateur_matin"), "fiche:mediateur_matin", "Médiateur du matin")
                poser(cells[4], D.mediateur(), "fiche:mediateur_am", "Médiateur de l'après-midi")
        elif libelle in valeurs and len(cells) >= 2:
            poser(cells[-1], valeurs[libelle], f"fiche:{libelle}", cells[0].text.strip())

    # 3. Emploi du temps (deuxième tableau)
    if len(doc.tables) > 1:
        edt = doc.tables[1]
        entetes = [c.text.strip().lower() for c in edt.rows[0].cells]
        lignes = {r.cells[0].text.strip().lower(): r for r in edt.rows[1:]}
        modele_style = lignes["matin"].cells[1] if "matin" in lignes else None

        matins = _matins(s.get("matin_texte"))
        if matins and "matin" in lignes:
            for i, jour in enumerate(entetes):
                if jour.capitalize() in JOURS_SEMAINE:
                    poser(lignes["matin"].cells[i], matins.get(jour.capitalize(), "—"),
                          f"edt:{jour}:matin", f"Matin du {jour}", modele_style)

        if planning is not None:
            for moment in ("après-midi", "veillée"):
                ligne = lignes.get(moment)
                if ligne is None:
                    continue
                for jour in JOURS_ACTIVITES:
                    if jour not in entetes:
                        continue
                    acts = planning[jour][moment]
                    poser(ligne.cells[entetes.index(jour)], " + ".join(a["nom"] for a in acts) or "…",
                          f"edt:{jour}:{moment}", f"{moment.capitalize()} du {jour}", modele_style)

        if planning is not None and pluie is not None:
            n = len(edt.rows)
            ligne = _ligne_pluie_edt(edt, entetes)
            if len(edt.rows) > n:
                remplis.append("Ligne « Si pluie » de l'emploi du temps")
            if ligne is not None:
                noms = " + ".join(a["nom"] for a in pluie)
                poser(ligne.cells[entetes.index(JOURS_ACTIVITES[0])],
                      f"{noms} ({MENTION_PLUIE})" if noms else "…", "edt:pluie", "Activité si pluie", modele_style)

    # 4. Détail des activités (troisième tableau)
    if planning is not None and len(doc.tables) > 2:
        if pluie is not None:
            n = len(doc.tables[2].rows)
            _bloc_pluie_detail(doc.tables[2])
            if len(doc.tables[2].rows) > n:
                remplis.append("Bloc « Si pluie » du détail des activités")
        for row in doc.tables[2].rows:
            cells = _cellules_distinctes(row)
            if len(cells) < 3:
                continue
            bloc = D.norm(cells[0].text)
            champ = "objectif_texte" if D.norm(cells[1].text).startswith("objectifs") else "description"
            court = "objectifs" if champ == "objectif_texte" else "descriptif"
            if bloc.startswith("veillee"):
                blocs = []
                for j in JOURS_ACTIVITES:
                    blocs += _blocs_detail(planning[j]["veillée"], champ, prefixe=f"{j.capitalize()} — ")
                poser(cells[2], _texte_blocs(blocs), f"detail:veillee:{court}", f"Veillée : {court}",
                      ecrire=lambda c, b=blocs: _ecrire_blocs(c, b))
            elif _est_pluie(bloc):
                if pluie is not None:
                    blocs = _blocs_detail(pluie, champ)
                    poser(cells[2], _texte_blocs(blocs), f"detail:pluie:{court}", f"Si pluie : {court}",
                          ecrire=lambda c, b=blocs: _ecrire_blocs(c, b))
            else:
                for j in JOURS_ACTIVITES:
                    if bloc.startswith(j):
                        blocs = _blocs_detail(planning[j]["après-midi"], champ)
                        poser(cells[2], _texte_blocs(blocs), f"detail:{j}:{court}",
                              f"{j.capitalize()} après-midi : {court}",
                              ecrire=lambda c, b=blocs: _ecrire_blocs(c, b))

    # 5. Ressources en autonomie
    if "ressources" in s:
        _maj_ressources(doc, s["ressources"], ecrits, nouveaux, remplis, conserves)

    if remplis:
        doc.save(chemin)
    return {"fichier": str(chemin), "remplis": remplis, "conserves": conserves, "ecrits": nouveaux}
