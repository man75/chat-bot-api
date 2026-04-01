# chatbot/constants.py

from schemas import ChatAction

CALENDLY_URL = "https://calendly.com/d/cppt-9xd-rv3/appel-10-min?month=2026-04"
PHONE_NUMBER = "tel:+33400000000"

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

ENERGIES = ["Essence", "Diesel", "Hybride", "Électrique", "GPL"]

MENU = (
    "Bonjour 👋 Bienvenue au garage.\n"
    "Choisissez une action en cliquant sur un bouton ci-dessous."
)
