"""Resolve PPT placeholder tokens to values for slide generation."""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.base import get_llm
from app.agents.tools.program_tools import get_program_summary
from app.agents.tools.hierarchy_tools import get_portfolio_spread
from app.agents.tools.adoption_tools import adoption_overview
from app.agents.tools.report_tools import utilization_report
from app.schemas.slides import GenerateSlidesRequest


AI_PROMPT = """You are writing a section for an executive PowerPoint slide.
Token: {token}
Section type: {kind}
Available data:
{data}

Write a concise (2-4 sentences) factual narrative for this section. No bullets, no markdown.
"""


async def _resolve_ai_token(token: str, data_summary: str) -> str:
    name = token.strip("{}")
    kind = name.lower().replace("_", " ")
    llm = get_llm(temperature=0.3)
    msg = AI_PROMPT.format(token=token, kind=kind, data=data_summary)
    try:
        resp = await llm.ainvoke([HumanMessage(content=msg)])
        return resp.content if hasattr(resp, "content") else str(resp)
    except Exception as e:
        return f"(AI generation failed: {e})"


def _format_table(rows: list[dict]) -> str:
    if not rows:
        return "(no data)"
    keys = list(rows[0].keys())
    lines = [" | ".join(keys)]
    for r in rows:
        lines.append(" | ".join(str(r.get(k, "")) for k in keys))
    return "\n".join(lines)


async def resolve_placeholders(
    placeholders: list[dict],
    request: GenerateSlidesRequest,
    db: AsyncSession,
) -> dict[str, str]:
    """Resolve every {{TOKEN}} to its string value."""
    data_map: dict[str, str] = {}

    program_summary = {}
    portfolio_spread: list[dict] = []
    if request.program_id:
        program_summary = await get_program_summary(db, str(request.program_id))
        portfolio_spread = await get_portfolio_spread(db, str(request.program_id))

    adoption = await adoption_overview(db)
    utilization = await utilization_report(db)

    data_summary_blob = (
        f"Program: {program_summary}\n"
        f"Portfolio spread: {portfolio_spread}\n"
        f"Adoption: {adoption}\n"
        f"Utilization: {utilization}\n"
        f"Period: {request.period}\n"
    )

    for p in placeholders:
        token = p["token"]
        ptype = p["type"]
        name = token.strip("{}")

        if ptype == "auto":
            if "DATE" in name:
                data_map[token] = datetime.utcnow().strftime("%Y-%m-%d")
            elif "PERIOD" in name or "QUARTER" in name:
                data_map[token] = request.period or _current_quarter()
            else:
                data_map[token] = ""
        elif ptype == "data":
            if "PROGRAM_NAME" in name:
                data_map[token] = program_summary.get("name", "")
            elif "STATUS" in name:
                data_map[token] = program_summary.get("status", "")
            elif "DESCRIPTION" in name:
                data_map[token] = program_summary.get("description", "") or ""
            else:
                data_map[token] = str(program_summary.get(name.lower(), ""))
        elif ptype == "table":
            if "SPREAD" in name:
                data_map[token] = _format_table(portfolio_spread)
            elif "UTIL" in name:
                data_map[token] = _format_table(utilization)
            elif "ADOPT" in name:
                data_map[token] = _format_table(adoption)
            else:
                data_map[token] = _format_table(portfolio_spread)
        elif ptype == "chart":
            data_map[token] = "(chart placeholder)"
        elif ptype == "ai":
            data_map[token] = await _resolve_ai_token(token, data_summary_blob)
        else:
            data_map[token] = ""

    return data_map


def _current_quarter() -> str:
    now = datetime.utcnow()
    q = (now.month - 1) // 3 + 1
    return f"Q{q} {now.year}"
