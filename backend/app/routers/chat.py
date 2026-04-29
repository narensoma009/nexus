import uuid
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.entra import get_current_user
from app.models.resource import UserRole
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatSession

router = APIRouter()

# In-memory session store for MVP
_sessions: dict[str, dict] = {}


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    data: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(get_current_user),
):
    from app.agents.platform_agent import run_platform_agent

    session_id = data.session_id or str(uuid.uuid4())
    session = _sessions.setdefault(session_id, {
        "user_oid": user.entra_oid,
        "created_at": datetime.utcnow(),
        "messages": [],
    })
    session["messages"].append({"role": "user", "content": data.message, "ts": datetime.utcnow().isoformat()})

    reply, sources = await run_platform_agent(
        message=data.message,
        history=session["messages"],
        context=data.context or {},
        user=user,
        db=db,
    )
    session["messages"].append({"role": "assistant", "content": reply, "ts": datetime.utcnow().isoformat()})
    return ChatMessageResponse(session_id=session_id, reply=reply, sources=sources)


@router.get("/sessions")
async def list_sessions(user: UserRole = Depends(get_current_user)):
    return [
        {"session_id": sid, "created_at": s["created_at"], "message_count": len(s["messages"])}
        for sid, s in _sessions.items() if s["user_oid"] == user.entra_oid
    ]


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(session_id: str, user: UserRole = Depends(get_current_user)):
    s = _sessions.get(session_id)
    if not s or s["user_oid"] != user.entra_oid:
        from fastapi import HTTPException
        raise HTTPException(404, "Session not found")
    return ChatSession(
        session_id=session_id,
        user_oid=s["user_oid"],
        created_at=s["created_at"],
        messages=s["messages"],
    )
