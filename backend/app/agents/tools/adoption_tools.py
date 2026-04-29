from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def adoption_overview(db: AsyncSession) -> list[dict]:
    res = await db.execute(
        text(
            """
            SELECT tool.name AS tool, tool.vendor,
                   COUNT(DISTINCT l.resource_id) AS users,
                   SUM(CASE WHEN l.adoption_stage = 'embedded' THEN 1 ELSE 0 END) AS embedded,
                   SUM(CASE WHEN l.adoption_stage = 'active' THEN 1 ELSE 0 END) AS active
            FROM ai_tools tool
            LEFT JOIN ai_tool_licenses l ON l.tool_id = tool.id
            GROUP BY tool.name, tool.vendor
            """
        )
    )
    return [dict(r._mapping) for r in res.fetchall()]


async def adoption_by_team(db: AsyncSession, team_id: str) -> list[dict]:
    res = await db.execute(
        text(
            """
            WITH RECURSIVE team_tree AS (
                SELECT id FROM teams WHERE id = :tid
                UNION ALL
                SELECT t.id FROM teams t JOIN team_tree tt ON t.parent_team_id = tt.id
            )
            SELECT tool.name AS tool, l.adoption_stage, COUNT(*) AS users
            FROM ai_tool_licenses l
            JOIN resources r ON r.id = l.resource_id
            JOIN ai_tools tool ON tool.id = l.tool_id
            WHERE r.team_id IN (SELECT id FROM team_tree)
            GROUP BY tool.name, l.adoption_stage
            """
        ),
        {"tid": team_id},
    )
    return [dict(r._mapping) for r in res.fetchall()]
