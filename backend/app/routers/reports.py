import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.entra import get_current_user
from app.models.resource import UserRole

router = APIRouter()


@router.get("/portfolio-summary")
async def portfolio_summary(db: AsyncSession = Depends(get_db), user: UserRole = Depends(get_current_user)):
    res = await db.execute(
        text(
            """
            SELECT p.id, p.name,
                   COUNT(DISTINCT t.id) AS team_count,
                   COUNT(DISTINCT r.id) AS resource_count
            FROM portfolios p
            LEFT JOIN teams t ON t.portfolio_id = p.id
            LEFT JOIN resources r ON r.team_id = t.id AND r.is_active = true
            GROUP BY p.id, p.name
            ORDER BY p.name
            """
        )
    )
    return [dict(r._mapping) for r in res.fetchall()]


@router.get("/resource-utilization")
async def resource_utilization(db: AsyncSession = Depends(get_db), user: UserRole = Depends(get_current_user)):
    res = await db.execute(
        text(
            """
            SELECT t.id AS team_id, t.name AS team_name,
                   AVG(ra.allocation_pct) AS avg_allocation,
                   COUNT(DISTINCT r.id) AS resource_count
            FROM teams t
            LEFT JOIN resources r ON r.team_id = t.id AND r.is_active = true
            LEFT JOIN resource_assignments ra ON ra.resource_id = r.id
            GROUP BY t.id, t.name
            ORDER BY avg_allocation DESC NULLS LAST
            """
        )
    )
    return [dict(r._mapping) for r in res.fetchall()]


@router.get("/ai-adoption-report")
async def ai_adoption_report(db: AsyncSession = Depends(get_db), user: UserRole = Depends(get_current_user)):
    res = await db.execute(
        text(
            """
            SELECT tool.name AS tool, tool.vendor, tool.category,
                   COUNT(DISTINCT l.resource_id) AS licensed_users,
                   SUM(CASE WHEN l.adoption_stage IN ('active', 'embedded') THEN 1 ELSE 0 END) AS active_users
            FROM ai_tools tool
            LEFT JOIN ai_tool_licenses l ON l.tool_id = tool.id
            GROUP BY tool.id, tool.name, tool.vendor, tool.category
            """
        )
    )
    return [dict(r._mapping) for r in res.fetchall()]


@router.post("/export")
async def export_report(payload: dict, db: AsyncSession = Depends(get_db),
                        user: UserRole = Depends(get_current_user)):
    rtype = payload.get("type", "portfolio-summary")
    if rtype == "portfolio-summary":
        rows = await portfolio_summary(db, user)
    elif rtype == "resource-utilization":
        rows = await resource_utilization(db, user)
    else:
        rows = await ai_adoption_report(db, user)

    if not rows:
        return StreamingResponse(io.BytesIO(b""), media_type="text/csv")

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    for r in rows:
        writer.writerow({k: ("" if v is None else v) for k, v in r.items()})
    return StreamingResponse(
        io.BytesIO(buf.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{rtype}.csv"'},
    )
