from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_team_members(db: AsyncSession, team_id: str) -> list[dict]:
    """All members of a team including sub-teams (recursive)."""
    result = await db.execute(
        text(
            """
            WITH RECURSIVE team_tree AS (
                SELECT id FROM teams WHERE id = :team_id
                UNION ALL
                SELECT t.id FROM teams t
                JOIN team_tree tt ON t.parent_team_id = tt.id
            )
            SELECT r.name, r.role, r.email
            FROM resources r
            JOIN team_tree tt ON r.team_id = tt.id
            WHERE r.is_active = true
            """
        ),
        {"team_id": team_id},
    )
    return [dict(r._mapping) for r in result.fetchall()]


async def get_portfolio_spread(db: AsyncSession, program_id: str) -> list[dict]:
    """Portfolio spread for a program."""
    result = await db.execute(
        text(
            """
            SELECT p.name AS portfolio, COUNT(DISTINCT r.id) AS resource_count
            FROM programs prog
            JOIN projects proj ON proj.program_id = prog.id
            JOIN workstreams ws ON ws.project_id = proj.id
            JOIN resource_assignments ra ON ra.workstream_id = ws.id
            JOIN resources r ON r.id = ra.resource_id
            JOIN teams t ON r.team_id = t.id
            LEFT JOIN sub_portfolios sp ON t.sub_portfolio_id = sp.id
            JOIN portfolios p ON p.id = COALESCE(t.portfolio_id, sp.portfolio_id)
            WHERE prog.id = :program_id
            GROUP BY p.name
            ORDER BY resource_count DESC
            """
        ),
        {"program_id": program_id},
    )
    return [dict(r._mapping) for r in result.fetchall()]
