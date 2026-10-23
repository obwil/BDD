# =============================================================================
# mails.py
# =============================================================================
# Rédaction des mails à l'enseignant, à partir des informations du séjour (Doc 3).
# Trois modèles : invitation à un appel, envoi du récapitulatif, relance.
# Les disponibilités sont à préciser à chaque fois : elles sont fournies à l'appel.
# =============================================================================

import re
from typing import Optional, Tuple

import doc3 as D

MODELES = {
    "invitation": "Invitation à l'appel",
    "recapitulatif": "Envoi du récapitulatif",
    "relance": "Relance",
}

A_PRECISER = "[à préciser]"


def civilite(enseignants: Optional[str]) -> str:
    """« Mme Braun » → « Madame Braun » ; « Mmes Fumey et Kruba » → « Mesdames Fumey et Kruba »."""
    s = (enseignants or "").strip()
    m = re.match(r"^(mmes|mme|mm|mr|m)\.?\s+(.*)$", s, re.I)
    if not m:
        return s
    pref = {"mmes": "Mesdames", "mme": "Madame", "mm": "Messieurs", "mr": "Monsieur", "m": "Monsieur"}[m.group(1).lower()]
    return f"{pref} {m.group(2).strip()}"


def dates_mail(s: dict) -> str:
    """« 28-09 au 02-10 », comme dans l'ancien modèle."""
    d1, d2 = s["date_debut"], s["date_fin"]
    return f"{d1[8:10]}-{d1[5:7]} au {d2[8:10]}-{d2[5:7]}"


def _dispos(disponibilites: Optional[str]) -> str:
    d = (disponibilites or "").strip()
    if not d:
        return f"Mes disponibilités sont : {A_PRECISER}"
    return "Mes disponibilités sont les suivantes :\n" + d


def rediger(modele: str, s: dict, disponibilites: Optional[str] = None, appel_fait: bool = False) -> Tuple[str, str]:
    """Retourne (objet, corps). Pour une relance : relance du rendez-vous tant que l'appel n'a pas eu lieu,
    puis relance sur le récapitulatif."""
    if modele not in MODELES:
        raise ValueError(f"Modèle inconnu : {modele}")
    civ, dates, med = civilite(s.get("enseignant")), dates_mail(s), D.mediateur()
    politesse = "Cordialement,\n" + med

    if modele == "invitation":
        objet = f"Votre séjour à Chamagnieu du {dates}"
        corps = (
            f"Bonjour {civ},\n\n"
            f"Je suis {med}, médiateur référent pour le projet de votre classe de découverte à l'éco-centre "
            f"de Chamagnieu, du {dates}.\n\n"
            "Je vous propose de convenir d'un rendez-vous téléphonique pour discuter du séjour et établir le "
            "planning de la semaine en fonction de vos thématiques et de vos objectifs.\n\n"
            f"{_dispos(disponibilites)}\n\n"
            "Dans l'attente de vous lire, je vous souhaite une belle semaine.\n\n"
            f"{politesse}"
        )
    elif modele == "recapitulatif":
        objet = f"Récapitulatif de votre séjour à Chamagnieu du {dates}"
        corps = (
            f"Bonjour {civ},\n\n"
            "Merci pour notre échange. Vous trouverez ci-joint le récapitulatif du projet de votre classe à "
            f"l'éco-centre de Chamagnieu, du {dates} : l'emploi du temps de la semaine, les activités prévues "
            "les après-midis et les veillées, et les objectifs pédagogiques.\n\n"
            "N'hésitez pas à me faire part de vos remarques ou des ajustements que vous souhaiteriez.\n\n"
            f"{politesse}"
        )
    elif not appel_fait:  # relance : rendez-vous téléphonique
        objet = f"Rendez-vous téléphonique : séjour à Chamagnieu du {dates}"
        corps = (
            f"Bonjour {civ},\n\n"
            f"Je me permets de revenir vers vous au sujet du séjour de votre classe à l'éco-centre de "
            f"Chamagnieu, du {dates}. Nous n'avons pas encore pu échanger par téléphone pour établir le "
            "planning de la semaine.\n\n"
            f"{_dispos(disponibilites)}\n\n"
            "Dans l'attente de vous lire, je vous souhaite une belle semaine.\n\n"
            f"{politesse}"
        )
    else:  # relance : retour sur le récapitulatif
        objet = f"Votre retour sur le séjour à Chamagnieu du {dates}"
        corps = (
            f"Bonjour {civ},\n\n"
            f"Je me permets de revenir vers vous au sujet du récapitulatif du séjour de votre classe à "
            f"l'éco-centre de Chamagnieu, du {dates}. Avez-vous pu en prendre connaissance ?\n\n"
            "Je reste disponible pour tout ajustement.\n\n"
            "Dans l'attente de vous lire, je vous souhaite une belle semaine.\n\n"
            f"{politesse}"
        )
    return objet, corps
