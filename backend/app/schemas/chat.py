import uuid
from datetime import datetime
from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    message: str
    session_id: str | None = None
    context: dict | None = None


class ChatMessageResponse(BaseModel):
    session_id: str
    reply: str
    sources: list[dict] = []


class ChatSession(BaseModel):
    session_id: str
    user_oid: str
    created_at: datetime
    messages: list[dict] = []
