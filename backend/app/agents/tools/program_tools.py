from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def list_programs(db: AsyncSession) -> list[dict]:
    res = await db.execute(text("SELECT id, name, status, description FROM programs"))
    return [dict(r._mapping) for r in res.fetchall()]


async def get_program_summary(db: AsyncSession, program_id: str) -> dict:
    res = await db.execute(
        text(
            """
            SELECT prog.name, prog.status, prog.description,
                   COUNT(DISTINCT proj.id) AS project_count,
                   COUNT(DISTINCT ws.id) AS workstream_count,
                   COUNT(DISTINCT ra.resource_id) AS resource_count
            FROM programs prog
            LEFT JOIN projects proj ON proj.program_id = prog.id
            LEFT JOIN workstreams ws ON ws.project_id = proj.id
            LEFT JOIN resource_assignments ra ON ra.workstream_id = ws.id
            WHERE prog.id = :pid
            GROUP BY prog.name, prog.status, prog.description
            """
        ),
        {"pid": program_id},
    )
    row = res.fetchone()
    return dict(row._mapping) if row else {}
