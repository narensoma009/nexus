"""Conversational LangGraph agent for the platform.

Routes: hierarchy / program / adoption / general.
1. retrieve — pgvector RAG
2. query_db — call appropriate DB tool based on routing
3. generate — LLM grounded answer
"""
from typing import TypedDict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import get_llm
from app.agents.tools.hierarchy_tools import get_team_members, get_portfolio_spread
from app.agents.tools.program_tools import list_programs, get_program_summary
from app.agents.tools.adoption_tools import adoption_overview, adoption_by_team
from app.agents.tools.report_tools import utilization_report
from app.services.embedding_service import similarity_search
from app.models.resource import UserRole


SYSTEM_PROMPT = """You are an AI assistant for the Accenture AT&T account internal platform.
You have access to live data about programs, portfolios, teams, resources, and AI adoption.
Answer questions concisely and factually using only the retrieved context below.
If the data doesn't support an answer, say so clearly.
Never invent names, numbers, or statuses.

User scope: {scope}

Context retrieved from the platform:
{context}
"""


def _classify(message: str) -> str:
    msg = message.lower()
    if any(k in msg for k in ["adoption", "tool", "copilot", "license"]):
        return "adoption"
    if any(k in msg for k in ["program", "project", "workstream", "milestone"]):
        return "program"
    if any(k in msg for k in ["team", "portfolio", "resource", "member", "roster"]):
        return "hierarchy"
    if any(k in msg for k in ["utilization", "allocation", "report"]):
        return "report"
    return "general"


async def _retrieve_context(db: AsyncSession, message: str, route: str, ctx: dict) -> tuple[str, list[dict]]:
    parts: list[str] = []
    sources: list[dict] = []

    try:
        rag = await similarity_search(db, message, k=4)
        for d in rag:
            parts.append(f"[{d.entity_type}:{d.entity_id}] {d.content}")
            sources.append({"type": d.entity_type, "id": str(d.entity_id)})
    except Exception:
        pass

    try:
        if route == "program":
            program_id = ctx.get("program_id")
            if program_id:
                summary = await get_program_summary(db, program_id)
                parts.append(f"Program summary: {summary}")
                spread = await get_portfolio_spread(db, program_id)
                parts.append(f"Portfolio spread: {spread}")
            else:
                progs = await list_programs(db)
                parts.append(f"Programs: {progs}")
        elif route == "adoption":
            team_id = ctx.get("team_id")
            if team_id:
                parts.append(f"Team adoption: {await adoption_by_team(db, team_id)}")
            else:
                parts.append(f"Adoption overview: {await adoption_overview(db)}")
        elif route == "hierarchy":
            team_id = ctx.get("team_id")
            if team_id:
                parts.append(f"Team members: {await get_team_members(db, team_id)}")
        elif route == "report":
            parts.append(f"Utilization: {await utilization_report(db)}")
    except Exception as e:
        parts.append(f"(tool error: {e})")

    return "\n\n".join(parts) if parts else "(no context retrieved)", sources


async def run_platform_agent(
    message: str,
    history: list[dict],
    context: dict,
    user: UserRole,
    db: AsyncSession,
) -> tuple[str, list[dict]]:
    route = _classify(message)
    ctx_text, sources = await _retrieve_context(db, message, route, context)

    scope = f"role={user.role}, scope_id={user.scope_id}"
    system = SYSTEM_PROMPT.format(scope=scope, context=ctx_text)

    llm = get_llm()
    messages = [SystemMessage(content=system)]
    for msg in history[-6:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
    messages.append(HumanMessage(content=message))

    try:
        resp = await llm.ainvoke(messages)
        reply = resp.content if hasattr(resp, "content") else str(resp)
    except Exception as e:
        reply = f"LLM error: {e}"

    return reply, sources
