# routes/chat.py

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Widget, Conversation, Message
from schemas import ChatRequest, ChatResponse
from chatbot.chatbot import generate_reply
from chatbot.conversation_state import ConversationState, Step

router = APIRouter()
logger = logging.getLogger(__name__)


LEAD_REQUIRED_FIELDS = [
    "nom",
    "prenom",
    "marque",
    "modele",
    "matricule",
    "sujet_devis",
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _log_lead_if_complete(state: ConversationState, conversation_id: str, widget_id: str) -> None:
    if state.step != Step.DEVIS_DONE:
        return

    missing = [field for field in LEAD_REQUIRED_FIELDS if not state.collected.get(field)]
    if missing:
        logger.warning(
            "lead_incomplete conversation_id=%s widget_id=%s missing=%s collected=%s",
            conversation_id,
            widget_id,
            missing,
            state.collected,
        )
        return

    logger.info(
        "lead_captured conversation_id=%s widget_id=%s nom=%s prenom=%s marque=%s modele=%s matricule=%s sujet_devis=%s",
        conversation_id,
        widget_id,
        state.collected.get("nom"),
        state.collected.get("prenom"),
        state.collected.get("marque"),
        state.collected.get("modele"),
        state.collected.get("matricule"),
        state.collected.get("sujet_devis"),
    )


@router.post("/chat/message", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    widget = db.query(Widget).filter(Widget.id == request.widgetId).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")

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

    state = ConversationState.from_json(conversation.state_json) \
        if getattr(conversation, "state_json", None) else ConversationState()

    user_msg = Message(conversation_id=conversation.id, role="user", content=request.message)
    db.add(user_msg)

    reply_text, action, quick_replies = generate_reply(request.message, state)

    conversation.state_json = state.to_json()

    _log_lead_if_complete(
        state=state,
        conversation_id=str(conversation.id),
        widget_id=request.widgetId,
    )

    bot_msg = Message(conversation_id=conversation.id, role="bot", content=reply_text)
    db.add(bot_msg)
    db.commit()

    return ChatResponse(
        reply=reply_text,
        conversationId=str(conversation.id),
        action=action,
        quickReplies=quick_replies
    )
