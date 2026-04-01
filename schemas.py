# schemas.py

from typing import Optional, Literal
from pydantic import BaseModel


class ChatAction(BaseModel):
    type: Literal["link", "phone"]
    label: str
    url: str


class ChatRequest(BaseModel):
    widgetId: str
    conversationId: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    reply: str
    conversationId: str
    action: Optional[ChatAction] = None

    # Front compatibility:
    # - quickReplies (camelCase)
    # - quick_replies (snake_case)
    # - buttons (generic fallback)
    quickReplies: Optional[list[str]] = None
    quick_replies: Optional[list[str]] = None
    buttons: Optional[list[str]] = None
