import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.entra import get_current_user
from app.auth.rbac import require_role, Role
from app.models.ai_adoption import AITool, AIToolLicense, AIToolUsage
from app.models.resource import Resource, UserRole
from app.schemas.ai_adoption import (
    AIToolCreate, AIToolOut,
    AIToolLicenseCreate, AIToolLicenseUpdate, AIToolLicenseOut,
    AIToolUsageCreate, AIToolUsageOut,
    AdoptionSummary, HeatmapCell, TrendPoint,
)

router = APIRouter()

STAGE_SCORES = {"piloting": 1, "onboarded": 2, "active": 3, "embedded": 4}


@router.get("/tools", response_model=list[AIToolOut])
async def list_tools(db: AsyncSession = Depends(get_db), user: UserRole = Depends(get_current_user)):
    res = await db.execute(select(AITool))
    return res.scalars().all()


@router.post("/tools", response_model=AIToolOut)
async def create_tool(
    data: AIToolCreate, db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.ACCOUNT_ADMIN)),
):
    t = AITool(**data.model_dump())
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t


@router.get("/tools/{tool_id}", response_model=AIToolOut)
async def get_tool(tool_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                   user: UserRole = Depends(get_current_user)):
    t = await db.get(AITool, tool_id)
    if not t:
        raise HTTPException(404, "Tool not found")
    return t


@router.put("/tools/{tool_id}", response_model=AIToolOut)
async def update_tool(
    tool_id: uuid.UUID, data: AIToolCreate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.ACCOUNT_ADMIN)),
):
    t = await db.get(AITool, tool_id)
    if not t:
        raise HTTPException(404, "Tool not found")
    for k, v in data.model_dump().items():
        setattr(t, k, v)
    await db.commit()
    await db.refresh(t)
    return t


@router.post("/tools/{tool_id}/licenses", response_model=AIToolLicenseOut)
async def assign_license(
    tool_id: uuid.UUID, data: AIToolLicenseCreate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PORTFOLIO_LEAD)),
):
    payload = data.model_dump()
    payload["tool_id"] = tool_id
    lic = AIToolLicense(**payload)
    db.add(lic)
    await db.commit()
    await db.refresh(lic)
    return lic


@router.put("/licenses/{license_id}", response_model=AIToolLicenseOut)
async def update_license(
    license_id: uuid.UUID, data: AIToolLicenseUpdate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.TEAM_LEAD)),
):
    lic = await db.get(AIToolLicense, license_id)
    if not lic:
        raise HTTPException(404, "License not found")
    lic.adoption_stage = data.adoption_stage
    await db.commit()
    await db.refresh(lic)
    return lic


@router.post("/usage", response_model=AIToolUsageOut)
async def log_usage(
    data: AIToolUsageCreate, db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(get_current_user),
):
    u = AIToolUsage(**data.model_dump())
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u


async def _team_ids_for_portfolio(db: AsyncSession, portfolio_id: uuid.UUID | None) -> list[str] | None:
    """Returns list of team IDs scoped to portfolio, or None for unfiltered."""
    if portfolio_id is None:
        return None
    from app.utils.hierarchy_utils import get_team_ids_under_portfolio
    return await get_team_ids_under_portfolio(db, str(portfolio_id))


@router.get("/summary", response_model=AdoptionSummary)
async def adoption_summary(
    portfolio_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(get_current_user),
):
    team_ids = await _team_ids_for_portfolio(db, portfolio_id)

    res_q = select(Resource.id).where(Resource.is_active == True)
    lic_q = select(AIToolLicense)
    if team_ids is not None:
        if not team_ids:
            return AdoptionSummary(total_resources=0, active_users=0, active_pct=0.0,
                                   tools_tracked=0, avg_stage_score=0.0)
        res_q = res_q.where(Resource.team_id.in_(team_ids))
        scoped_resource_ids = [r for r in (await db.execute(res_q)).scalars().all()]
        lic_q = lic_q.where(AIToolLicense.resource_id.in_(scoped_resource_ids)) if scoped_resource_ids else lic_q.where(AIToolLicense.id == None)
        total_resources = len(scoped_resource_ids)
    else:
        total_resources = (await db.execute(select(func.count(Resource.id)).where(Resource.is_active == True))).scalar() or 0

    licenses = list((await db.execute(lic_q)).scalars().all())
    active_users = len({l.resource_id for l in licenses if l.adoption_stage in ("active", "embedded")})
    tool_ids_in_scope = {l.tool_id for l in licenses}
    tools_tracked = len(tool_ids_in_scope) if portfolio_id else (
        (await db.execute(select(func.count(AITool.id)))).scalar() or 0
    )
    avg_score = (sum(STAGE_SCORES.get(l.adoption_stage, 0) for l in licenses) / len(licenses)) if licenses else 0.0
    pct = (active_users / total_resources * 100) if total_resources else 0.0

    return AdoptionSummary(
        total_resources=total_resources,
        active_users=active_users,
        active_pct=round(pct, 2),
        tools_tracked=tools_tracked,
        avg_stage_score=round(avg_score, 2),
    )


@router.get("/heatmap", response_model=list[HeatmapCell])
async def heatmap(
    portfolio_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(get_current_user),
):
    team_ids = await _team_ids_for_portfolio(db, portfolio_id)
    if team_ids is not None and not team_ids:
        return []

    where = ""
    params: dict = {}
    if team_ids is not None:
        placeholders = ",".join(f":t{i}" for i in range(len(team_ids)))
        where = f"WHERE r.team_id IN ({placeholders})"
        params = {f"t{i}": tid for i, tid in enumerate(team_ids)}

    res = await db.execute(
        text(f"""
            SELECT t.id AS team_id, t.name AS team_name,
                   tool.id AS tool_id, tool.name AS tool_name,
                   l.adoption_stage AS stage,
                   COUNT(DISTINCT l.resource_id) AS user_count
            FROM ai_tool_licenses l
            JOIN resources r ON r.id = l.resource_id
            JOIN teams t ON r.team_id = t.id
            JOIN ai_tools tool ON tool.id = l.tool_id
            {where}
            GROUP BY t.id, t.name, tool.id, tool.name, l.adoption_stage
        """),
        params,
    )
    return [HeatmapCell(**dict(r._mapping)) for r in res.fetchall()]


@router.get("/trends", response_model=list[TrendPoint])
async def trends(
    portfolio_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(get_current_user),
):
    team_ids = await _team_ids_for_portfolio(db, portfolio_id)
    if team_ids is not None and not team_ids:
        return []

    where = ""
    params: dict = {}
    if team_ids is not None:
        placeholders = ",".join(f":t{i}" for i in range(len(team_ids)))
        where = f"WHERE r.team_id IN ({placeholders})"
        params = {f"t{i}": tid for i, tid in enumerate(team_ids)}

    res = await db.execute(
        text(f"""
            SELECT u.recorded_date AS date,
                   tool.id AS tool_id, tool.name AS tool_name,
                   SUM(u.sessions) AS sessions,
                   SUM(u.active_minutes) AS active_minutes
            FROM ai_tool_usages u
            JOIN ai_tools tool ON tool.id = u.tool_id
            JOIN resources r ON r.id = u.resource_id
            {where}
            GROUP BY u.recorded_date, tool.id, tool.name
            ORDER BY u.recorded_date
        """),
        params,
    )
    return [TrendPoint(**dict(r._mapping)) for r in res.fetchall()]
