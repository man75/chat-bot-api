# routes/chat.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Widget, Conversation, Message
from schemas import ChatRequest, ChatResponse
from chatbot.chatbot import generate_reply
from chatbot.conversation_state import ConversationState

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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

    reply_text, action = generate_reply(request.message, state)

    conversation.state_json = state.to_json()

    bot_msg = Message(conversation_id=conversation.id, role="bot", content=reply_text)
    db.add(bot_msg)
    db.commit()

    return ChatResponse(
        reply=reply_text,
        conversationId=str(conversation.id),
        action=action
    )