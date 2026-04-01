# chatbot/constants.py

from schemas import ChatAction

CALENDLY_URL = "https://calendly.com/d/cppt-9xd-rv3/appel-10-min?month=2026-04"
PHONE_NUMBER  = "tel:+33400000000"

CALENDLY_ACTION = ChatAction(
    type="link",
    label="Réserver un créneau",
    url=CALENDLY_URL
)

PHONE_ACTION = ChatAction(
    type="phone",
    label="Nous appeler",
    url=PHONE_NUMBER
)

ENERGIES = ["essence", "diesel", "hybride", "électrique", "gpl"]

MENU = (
    "Bonjour 👋 Bienvenue au garage ! Comment puis-je vous aider ?\n\n"
    "1️⃣  Prendre un rendez-vous\n"
    "2️⃣  Demander un devis\n"
    "3️⃣  Poser une question\n\n"
    "Tapez le numéro ou décrivez directement votre besoin."
)
