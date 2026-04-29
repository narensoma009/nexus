from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def utilization_report(db: AsyncSession) -> list[dict]:
    res = await db.execute(
        text(
            """
            SELECT t.name AS team, AVG(ra.allocation_pct) AS avg_alloc
            FROM teams t
            LEFT JOIN resources r ON r.team_id = t.id AND r.is_active = true
            LEFT JOIN resource_assignments ra ON ra.resource_id = r.id
            GROUP BY t.name
            ORDER BY avg_alloc DESC NULLS LAST
            """
        )
    )
    return [dict(r._mapping) for r in res.fetchall()]
