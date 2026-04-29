from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_descendant_team_ids(db: AsyncSession, team_id: str) -> list[str]:
    """Return team_id and all descendants via recursive CTE."""
    result = await db.execute(
        text(
            """
            WITH RECURSIVE team_tree AS (
                SELECT id FROM teams WHERE id = :team_id
                UNION ALL
                SELECT t.id FROM teams t
                JOIN team_tree tt ON t.parent_team_id = tt.id
            )
            SELECT id FROM team_tree
            """
        ),
        {"team_id": team_id},
    )
    return [str(r[0]) for r in result.fetchall()]


async def get_team_ids_under_portfolio(db: AsyncSession, portfolio_id: str) -> list[str]:
    """All team IDs (including sub-teams) belonging to a portfolio."""
    result = await db.execute(
        text(
            """
            WITH RECURSIVE root_teams AS (
                SELECT id FROM teams WHERE portfolio_id = :pid
                UNION
                SELECT t.id FROM teams t
                JOIN sub_portfolios sp ON t.sub_portfolio_id = sp.id
                WHERE sp.portfolio_id = :pid
            ),
            team_tree AS (
                SELECT id FROM root_teams
                UNION ALL
                SELECT t.id FROM teams t
                JOIN team_tree tt ON t.parent_team_id = tt.id
            )
            SELECT DISTINCT id FROM team_tree
            """
        ),
        {"pid": portfolio_id},
    )
    return [str(r[0]) for r in result.fetchall()]
