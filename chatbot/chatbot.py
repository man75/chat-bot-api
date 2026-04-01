from typing import Optional, Tuple

from chatbot.constants import MENU, PHONE_ACTION, CALENDLY_ACTION, ENERGIES
from schemas import ChatAction
from chatbot.conversation_state import ConversationState, Intent, Step


QuickReplies = Optional[list[str]]


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def _main_menu() -> Tuple[str, Optional[ChatAction], QuickReplies]:
    return MENU, None, ["Prise de RDV", "Demander un devis"]


def _start_lead_flow(state: ConversationState) -> Tuple[str, Optional[ChatAction], QuickReplies]:
    state.intent = Intent.DEVIS
    state.step = Step.COLLECT_NOM
    state.collected = {}
    return "Parfait, commençons. Quel est votre **nom** ?", None, None


def generate_reply(
    message: str,
    state: ConversationState,
) -> Tuple[str, Optional[ChatAction], QuickReplies]:
    msg = _normalize(message)

    if not msg:
        return "Je n'ai pas bien compris. Pouvez-vous reformuler ?", None, None

    if any(k in msg for k in {"bonjour", "bonsoir", "salut", "hello", "coucou", "menu", "start"}):
        state.intent = Intent.NONE
        state.step = None
        state.collected = {}
        return _main_menu()

    if state.intent == Intent.NONE:
        if any(k in msg for k in {"devis", "demander un devis"}):
            return _start_lead_flow(state)

        if any(k in msg for k in {"prise de rdv", "rdv", "rendez-vous", "rendez vous"}):
            return (
                "Très bien, vous pouvez réserver votre créneau en cliquant ici.",
                CALENDLY_ACTION,
                ["Demander un devis"],
            )

        return _main_menu()

    if state.step == Step.COLLECT_NOM:
        state.collected["nom"] = message.strip()
        state.step = Step.COLLECT_PRENOM
        return "Merci. Quel est votre **prénom** ?", None, None

    if state.step == Step.COLLECT_PRENOM:
        state.collected["prenom"] = message.strip()
        state.step = Step.DEVIS_MARQUE
        return "Quelle est la **marque** du véhicule ?", None, None

    if state.step == Step.DEVIS_MARQUE:
        state.collected["marque"] = message.strip()
        state.step = Step.DEVIS_MODELE
        return "Quel est le **modèle** du véhicule ?", None, None

    if state.step == Step.DEVIS_MODELE:
        state.collected["modele"] = message.strip()
        state.step = Step.DEVIS_MATRICULE
        return "Quel est le **numéro d'immatriculation** ?", None, None

    if state.step == Step.DEVIS_MATRICULE:
        state.collected["matricule"] = message.strip()
        state.step = Step.DEVIS_ENERGIE
        return "Choisissez l'énergie du véhicule :", None, ENERGIES

    if state.step == Step.DEVIS_ENERGIE:
        state.collected["energie"] = message.strip()
        state.step = Step.DEVIS_SUJET
        return "Quel est le **sujet du devis** (ex: vidange, freins, embrayage...) ?", None, None

    if state.step == Step.DEVIS_SUJET:
        state.collected["sujet_devis"] = message.strip()
        state.step = Step.DEVIS_DONE
        return (
            "Parfait ✅ Votre lead est complet et bien enregistré. Un conseiller vous rappelle rapidement.",
            PHONE_ACTION,
            ["Menu principal"],
        )

    if state.step == Step.DEVIS_DONE:
        state.intent = Intent.NONE
        state.step = None
        return _main_menu()

    return _main_menu()
