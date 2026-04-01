import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Widget, Conversation, Message
from schemas import ChatRequest, ChatResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_reply(message: str) -> str:
    msg = message.lower()

   # ── Salutations ────────────────────────────────────────────────
    if any(w in msg for w in ["bonjour", "bonsoir", "salut", "hello", "coucou"]):
        return (
            "Bonjour et bienvenue ! 👋 Je suis l'assistant du garage.\n\n"
            "Je peux vous renseigner sur :\n"
            "• Nos services (révision, freins, pneus, climatisation…)\n"
            "• Les tarifs et devis\n"
            "• La prise de rendez-vous\n"
            "• Les délais d'intervention\n\n"
            "Comment puis-je vous aider aujourd'hui ?"
        )

    # ── Contact & horaires ─────────────────────────────────────────
    if any(w in msg for w in ["horaire", "ouvert", "fermé", "heure", "quand vous"]):
        return (
            "🕐 Nos horaires d'ouverture :\n\n"
            "• Lundi – Vendredi : 8h00 – 18h30\n"
            "• Samedi : 8h00 – 12h30\n"
            "• Dimanche & jours fériés : fermé\n\n"
            "Vous pouvez nous appeler au 04 XX XX XX XX ou envoyer un e-mail à contact@garage.fr."
        )

    if any(w in msg for w in ["contact", "téléphone", "email", "adresse", "où êtes", "localisation", "comment venir"]):
        return (
            "📍 Vous pouvez nous joindre facilement :\n\n"
            "• Téléphone : 04 XX XX XX XX (Lun–Ven 8h–18h30)\n"
            "• E-mail : contact@garage.fr\n"
            "• Adresse : 12 rue des Mécaniciens, 69400 Villefranche-sur-Saône\n\n"
            "Un formulaire de contact est aussi disponible sur notre site. Réponse garantie sous 24h."
        )

    # ── Rendez-vous ────────────────────────────────────────────────
    if any(w in msg for w in ["rendez-vous", "rdv", "réserver", "réservation", "prendre rendez", "disponibilité", "créneau"]):
        return (
            "📅 Prendre rendez-vous est simple !\n\n"
            "Vous pouvez :\n"
            "1. Réserver en ligne directement sur notre site (disponible 24h/24)\n"
            "2. Nous appeler au 04 XX XX XX XX\n"
            "3. Passer directement au garage — nous ferons notre possible pour vous recevoir.\n\n"
            "Précisez le type d'intervention souhaitée et votre véhicule (marque, modèle, année) "
            "pour que nous préparions au mieux votre passage. 🔧"
        )

    # ── Tarifs & devis ─────────────────────────────────────────────
    if any(w in msg for w in ["prix", "tarif", "coût", "combien", "devis", "facturation", "gratuit"]):
        return (
            "💶 Nos tarifs varient selon le type d'intervention et votre véhicule.\n\n"
            "Exemples de fourchettes indicatives :\n"
            "• Vidange + filtre : à partir de 49 €\n"
            "• Remplacement plaquettes freins (essieu) : à partir de 79 €\n"
            "• Recharge climatisation : à partir de 69 €\n"
            "• Diagnostic électronique : 39 €\n\n"
            "Nous établissons un devis gratuit et détaillé avant toute intervention. "
            "Aucun travail ne commence sans votre accord. Quel service vous intéresse ?"
        )

    # ── Révision & entretien ───────────────────────────────────────
    if any(w in msg for w in ["révision", "entretien", "vidange", "filtre", "courroie distribution", "bougies"]):
        return (
            "🔧 L'entretien régulier est essentiel pour la longévité de votre véhicule.\n\n"
            "Nos prestations d'entretien incluent :\n"
            "• Vidange huile moteur + filtre à huile\n"
            "• Remplacement filtre à air, habitacle, carburant\n"
            "• Contrôle et remplacement bougies\n"
            "• Remplacement courroie de distribution (recommandé tous les 5 ans ou 120 000 km)\n"
            "• Vérification des niveaux (liquide de frein, refroidissement, direction)\n\n"
            "Révision constructeur ou entretien à la carte — nous nous adaptons à vos besoins. "
            "Souhaitez-vous un devis personnalisé ?"
        )

    # ── Pneumatiques ──────────────────────────────────────────────
    if any(w in msg for w in ["pneu", "roue", "gomme", "jante", "crevaison", "équilibrage", "parallélisme"]):
        return (
            "🚗 Pneus : nous proposons un large choix de marques (Michelin, Pirelli, Continental, Bridgestone…).\n\n"
            "Nos services pneumatiques :\n"
            "• Montage et équilibrage (2 roues ou pack 4 roues)\n"
            "• Permutation avant/arrière\n"
            "• Réparation de crevaison\n"
            "• Contrôle et réglage du parallélisme\n"
            "• Stockage de jantes saisonnières disponible\n\n"
            "Indiquez-nous la dimension de vos pneus (ex : 205/55 R16) "
            "pour que nous vérifiions nos disponibilités. 📦"
        )

    # ── Freinage ──────────────────────────────────────────────────
    if any(w in msg for w in ["frein", "plaquette", "disque", "frein à main", "abs", "pédale"]):
        return (
            "⚠️ Les freins sont un élément de sécurité critique — ne tardez pas si vous ressentez :\n"
            "• Un bruit strident ou métallique au freinage\n"
            "• Un allongement de la distance d'arrêt\n"
            "• Des vibrations dans la pédale\n"
            "• Le témoin ABS ou frein allumé au tableau de bord\n\n"
            "Nos interventions freinage :\n"
            "• Remplacement plaquettes et/ou disques (avant et arrière)\n"
            "• Purge et remplacement du liquide de frein\n"
            "• Réglage ou remplacement du frein à main\n\n"
            "Devis gratuit — intervention possible en 1 à 2 heures selon disponibilité. 🛠️"
        )

    # ── Climatisation ─────────────────────────────────────────────
    if any(w in msg for w in ["clim", "climatisation", "recharge", "froid", "chauffage", "ventilation"]):
        return (
            "❄️ Climatisation : une recharge annuelle (avant l'été) est recommandée.\n\n"
            "Nos services clim :\n"
            "• Recharge gaz réfrigérant (R134a ou R1234yf selon véhicule)\n"
            "• Contrôle d'étanchéité du circuit\n"
            "• Nettoyage et désinfection de l'habitacle (anti-bactérien)\n"
            "• Remplacement compresseur ou condenseur si nécessaire\n\n"
            "Tarif recharge standard à partir de 69 €. Comptez environ 1h d'intervention. "
            "Souhaitez-vous réserver ?"
        )

    # ── Batterie & électrique ──────────────────────────────────────
    if any(w in msg for w in ["batterie", "démarrage", "électrique", "alternateur", "démarreur", "ne démarre pas"]):
        return (
            "🔋 Problème électrique ou de démarrage ?\n\n"
            "Signes d'une batterie défaillante :\n"
            "• Démarrage lent ou difficile le matin\n"
            "• Voyant batterie allumé\n"
            "• Batterie de plus de 4–5 ans\n\n"
            "Nos interventions :\n"
            "• Diagnostic électrique complet\n"
            "• Remplacement batterie (en stock pour la plupart des véhicules)\n"
            "• Contrôle alternateur et démarreur\n"
            "• Codage batterie si requis (véhicules récents)\n\n"
            "Remplacement batterie possible sans rendez-vous en 30 minutes. Appelez-nous ! 📞"
        )

    # ── Diagnostic & panne ────────────────────────────────────────
    if any(w in msg for w in ["panne", "diagnostic", "voyant", "moteur", "bruit", "fumée", "odeur", "fuite"]):
        return (
            "🔍 Voyant allumé, bruit suspect ou comportement anormal ? Ne prenez pas de risques.\n\n"
            "Notre diagnostic électronique (valise OBD) lit les codes défauts de :\n"
            "• Moteur, boîte de vitesses\n"
            "• Système de freinage (ABS / ESP)\n"
            "• Airbag, climatisation, tableau de bord\n\n"
            "Tarif diagnostic : 39 € (déduit de la réparation si vous nous confiez le véhicule).\n\n"
            "Si votre véhicule est immobilisé, nous pouvons aussi vous orienter vers un service de "
            "remorquage partenaire. 🚛 Décrivez-nous le problème pour mieux vous conseiller."
        )

    # ── Contrôle technique ────────────────────────────────────────
    if any(w in msg for w in ["contrôle technique", "ct", "contre-visite", "procès-verbal"]):
        return (
            "📋 Contrôle technique : nous ne réalisons pas directement le contrôle, "
            "mais nous pouvons vous y préparer.\n\n"
            "Pré-contrôle technique gratuit chez nous :\n"
            "• Vérification des points souvent mis en défaut (éclairages, freins, pneus, fuite)\n"
            "• Réparations ciblées avant présentation au centre agréé\n"
            "• Assistance contre-visite si des travaux sont nécessaires\n\n"
            "Nous travaillons en partenariat avec un centre de contrôle technique à proximité. "
            "Voulez-vous qu'on vous oriente ?"
        )

    # ── Carrosserie ───────────────────────────────────────────────
    if any(w in msg for w in ["carrosserie", "rayure", "bosse", "débosselage", "peinture", "pare-choc", "accident", "sinistre"]):
        return (
            "🎨 Carrosserie et peinture : nous prenons en charge tout type de réparation.\n\n"
            "• Débosselage sans peinture (PDR) pour les petits chocs\n"
            "• Retouches peinture et teintes à l'identique\n"
            "• Remplacement ou réparation de pare-chocs\n"
            "• Prise en charge assurance et gestion du dossier sinistre\n\n"
            "Nous travaillons en agréé avec la plupart des assureurs. "
            "Apportez votre véhicule pour un devis carrosserie gratuit. 📸"
        )

    # ── Pare-brise & vitres ───────────────────────────────────────
    if any(w in msg for w in ["pare-brise", "vitre", "fissure", "impact", "bris de glace", "rétroviseur"]):
        return (
            "🪟 Remplacement ou réparation de vitrage automobile.\n\n"
            "• Réparation d'impact (étoile < 2 cm) : rapide, économique, souvent pris en charge à 100% par l'assurance\n"
            "• Remplacement pare-brise : toutes marques, recalibrage caméra ADAS inclus si nécessaire\n"
            "• Remplacement vitre latérale ou lunette arrière\n\n"
            "Intervention possible le jour même selon disponibilité. "
            "La prise en charge bris de glace est gratuite avec la plupart des assurances (sans franchise). "
            "Avez-vous une assurance tous risques ?"
        )

    # ── Délais ────────────────────────────────────────────────────
    if any(w in msg for w in ["délai", "combien de temps", "durée", "prêt", "récupérer", "attendre"]):
        return (
            "⏱️ Délais indicatifs selon l'intervention :\n\n"
            "• Vidange / filtre : 45 min à 1h\n"
            "• Pneus (4 roues) : 1h à 1h30\n"
            "• Plaquettes de frein : 1h à 2h\n"
            "• Recharge climatisation : 1h\n"
            "• Remplacement batterie : 30 min\n"
            "• Réparation carrosserie : 1 à 5 jours selon étendue\n\n"
            "Pour les interventions longues, nous vous proposons un véhicule de prêt sous réserve de disponibilité. "
            "Quel travail souhaitez-vous effectuer ?"
        )

    # ── Garantie ──────────────────────────────────────────────────
    if any(w in msg for w in ["garantie", "garanti", "défaut", "réclamation", "après travaux"]):
        return (
            "✅ Toutes nos réparations sont garanties :\n\n"
            "• Pièces : garantie constructeur (généralement 1 à 2 ans)\n"
            "• Main d'œuvre : 6 mois garantis sur nos interventions\n"
            "• Peinture carrosserie : 2 ans\n\n"
            "En cas de problème après une intervention, contactez-nous immédiatement. "
            "Nous reprenons le véhicule en priorité et sans frais si le problème est lié à notre travail. 🤝"
        )

    # ── Véhicule de prêt ──────────────────────────────────────────
    if any(w in msg for w in ["prêt", "voiture de prêt", "véhicule de remplacement", "louer", "mobilité"]):
        return (
            "🚙 Véhicule de prêt : nous mettons à disposition des véhicules de courtoisie "
            "pour les interventions longues (carrosserie, révision majeure…).\n\n"
            "• Gratuit pour les interventions > 4h ou sur devis validé\n"
            "• Sous réserve de disponibilité (à réserver à l'avance)\n"
            "• Permis B requis, conducteur principal uniquement\n\n"
            "Mentionnez-le lors de la prise de rendez-vous pour garantir la disponibilité. 📅"
        )

    # ── Paiement ──────────────────────────────────────────────────
    if any(w in msg for w in ["payer", "paiement", "cb", "carte", "chèque", "virement", "espèces", "facilité", "financement"]):
        return (
            "💳 Modes de paiement acceptés :\n\n"
            "• Carte bancaire (CB, Visa, Mastercard)\n"
            "• Espèces (jusqu'à 1 000 €)\n"
            "• Chèque\n"
            "• Virement bancaire\n"
            "• Paiement en plusieurs fois disponible (sous conditions) pour les factures > 300 €\n\n"
            "Pour les prises en charge assurance, nous gérons le dossier directement avec votre assureur. "
            "Plus de détails à l'accueil ou par téléphone. 📞"
        )

    # ── Urgence & dépannage ───────────────────────────────────────
    if any(w in msg for w in ["urgent", "urgence", "dépannage", "remorquage", "immobilisé", "en panne sur la route"]):
        return (
            "🚨 Vous êtes en panne ou immobilisé ? Voici comment réagir :\n\n"
            "1. Mettez-vous en sécurité (triangle, gilet jaune)\n"
            "2. Appelez-nous au 04 XX XX XX XX — nous pouvons vous orienter ou intervenir rapidement\n"
            "3. Si besoin, nous faisons appel à notre partenaire remorquage disponible 7j/7\n\n"
            "Pour les pannes hors horaires, laissez un message ou envoyez un SMS : "
            "nous vous rappelons en priorité dès l'ouverture. Ne restez pas seul face à la panne ! 🛠️"
        )

    # ── Fallback ──────────────────────────────────────────────────
    return (
        "Merci pour votre message ! 🙏 Un de nos conseillers va examiner votre demande "
        "et vous répondre dans les plus brefs délais.\n\n"
        "Pour une réponse immédiate, n'hésitez pas à nous appeler directement au "
        "04 XX XX XX XX (Lun–Ven 8h–18h30, Sam 8h–12h30).\n\n"
        "Vous pouvez aussi préciser votre demande (ex : type d'intervention, marque et modèle du véhicule) "
        "pour que nous puissions mieux vous orienter. 🚗"
    )


@router.post("/chat/message", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # Vérifier widget
    widget = db.query(Widget).filter(Widget.id == request.widgetId).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

    # Conversation
    if request.conversationId:
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversationId
        ).first()
    else:
        conversation = None

    if not conversation:
        conversation = Conversation(widget_id=request.widgetId)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Message user
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_msg)

    # Réponse bot
    reply_text = generate_reply(request.message)

    bot_msg = Message(
        conversation_id=conversation.id,
        role="bot",
        content=reply_text
    )
    db.add(bot_msg)

    db.commit()

    return ChatResponse(
        reply=reply_text,
        conversationId=str(conversation.id)
    )