from typing import Optional, Tuple

from chatbot.constants import MENU, CALENDLY_ACTION, PHONE_ACTION
from schemas import ChatAction
from chatbot.conversation_state import ConversationState, Intent, Step


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def _is_yes(text: str) -> bool:
    return text in {"oui", "ok", "yes", "y", "d'accord", "dac", "bien sûr", "bien sur"}


def _is_no(text: str) -> bool:
    return text in {"non", "no", "n", "pas maintenant", "plus tard"}


def generate_reply(message: str, state: ConversationState) -> Tuple[str, Optional[ChatAction]]:
    msg = _normalize(message)

    if not msg:
        return "Je n'ai pas bien compris. Pouvez-vous reformuler ?", None

    if any(k in msg for k in {"bonjour", "bonsoir", "salut", "hello", "coucou", "menu"}):
        state.intent = Intent.NONE
        state.step = None
        state.collected = {}
        return MENU, None

    if state.intent == Intent.NONE:
        if msg in {"1", "rdv", "rendez-vous", "rendez vous", "rendezvous"}:
            state.intent = Intent.RDV
            state.step = Step.COLLECT_NOM
            return "Parfait 👍 Commençons. Quel est votre nom complet ?", None

        if msg in {"2", "devis"}:
            state.intent = Intent.DEVIS
            state.step = Step.COLLECT_NOM
            return "Très bien. Pour le devis, j'ai d'abord besoin de votre nom complet.", None

        if msg in {"3", "question", "aide"}:
            state.intent = Intent.QUESTION
            state.step = Step.COLLECT_NOM
            return "Bien sûr. Quel est votre nom complet ?", None

        if any(k in msg for k in {"prix", "tarif", "coût", "cout", "devis"}):
            state.intent = Intent.DEVIS
            state.step = Step.COLLECT_NOM
            return "Je peux vous aider pour un devis. Quel est votre nom complet ?", None

        if any(k in msg for k in {"rendez", "rdv", "créneau", "creneau", "disponible"}):
            state.intent = Intent.RDV
            state.step = Step.COLLECT_NOM
            return "Je vous aide à réserver un rendez-vous. Quel est votre nom complet ?", None

        return MENU, None

    if state.step == Step.COLLECT_NOM:
        state.collected["nom"] = message.strip()
        state.step = Step.COLLECT_TELEPHONE
        return "Merci. Quel est votre numéro de téléphone ?", None

    if state.step == Step.COLLECT_TELEPHONE:
        state.collected["telephone"] = message.strip()
        state.step = Step.COLLECT_MAIL
        return "Parfait. Quelle est votre adresse e-mail ?", None

    if state.step == Step.COLLECT_MAIL:
        state.collected["mail"] = message.strip()

        if state.intent == Intent.DEVIS:
            state.step = Step.DEVIS_MARQUE
            return "Merci. Quelle est la marque de votre véhicule ?", None

        if state.intent == Intent.RDV:
            state.step = Step.RDV_DONE
            return (
                "Merci ✅ Votre demande de rendez-vous est enregistrée. "
                "Souhaitez-vous réserver un créneau maintenant ?"
            ), CALENDLY_ACTION

        state.step = Step.QUESTION_DONE
        return (
            "Merci ✅ Un conseiller vous recontacte rapidement. "
            "Si c'est urgent, vous pouvez aussi nous appeler."
        ), PHONE_ACTION

    if state.step == Step.DEVIS_MARQUE:
        state.collected["marque"] = message.strip()
        state.step = Step.DEVIS_MODELE
        return "Quel est le modèle du véhicule ?", None

    if state.step == Step.DEVIS_MODELE:
        state.collected["modele"] = message.strip()
        state.step = Step.DEVIS_MATRICULE
        return "Quel est le numéro d'immatriculation ?", None

    if state.step == Step.DEVIS_MATRICULE:
        state.collected["matricule"] = message.strip()
        state.step = Step.DEVIS_ENERGIE
        return "Quelle est l'énergie du véhicule (essence, diesel, hybride, électrique) ?", None

    if state.step == Step.DEVIS_ENERGIE:
        state.collected["energie"] = message.strip()
        state.step = Step.DEVIS_DONE
        return (
            "Parfait ✅ Votre demande de devis est enregistrée. "
            "Souhaitez-vous être rappelé immédiatement ?"
        ), PHONE_ACTION

    if state.step in {Step.RDV_DONE, Step.DEVIS_DONE, Step.QUESTION_DONE}:
        if _is_yes(msg):
            if state.step == Step.RDV_DONE:
                return "Super, voici le lien pour réserver votre créneau :", CALENDLY_ACTION
            return "Très bien, vous pouvez nous appeler directement ici :", PHONE_ACTION

        if _is_no(msg):
            state.intent = Intent.NONE
            state.step = None
            state.collected = {}
            return "D'accord 🙂 Si besoin, tapez 'menu' pour recommencer.", None

        return "Répondez par 'oui' ou 'non' pour continuer.", None

    return MENU, None
