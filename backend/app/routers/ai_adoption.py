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


@router.get("/summary", response_model=AdoptionSummary)
async def adoption_summary(db: AsyncSession = Depends(get_db), user: UserRole = Depends(get_current_user)):
    total_resources = (await db.execute(select(func.count(Resource.id)).where(Resource.is_active == True))).scalar() or 0
    active_users = (await db.execute(
        select(func.count(func.distinct(AIToolLicense.resource_id)))
        .where(AIToolLicense.adoption_stage.in_(["active", "embedded"]))
    )).scalar() or 0
    tools_tracked = (await db.execute(select(func.count(AITool.id)))).scalar() or 0

    licenses = (await db.execute(select(AIToolLicense))).scalars().all()
    if licenses:
        avg_score = sum(STAGE_SCORES.get(l.adoption_stage, 0) for l in licenses) / len(licenses)
    else:
        avg_score = 0.0

    pct = (active_users / total_resources * 100) if total_resources else 0.0
    return AdoptionSummary(
        total_resources=total_resources,
        active_users=active_users,
        active_pct=round(pct, 2),
        tools_tracked=tools_tracked,
        avg_stage_score=round(avg_score, 2),
    )


@router.get("/heatmap", response_model=list[HeatmapCell])
async def heatmap(db: AsyncSession = Depends(get_db), user: UserRole = Depends(get_current_user)):
    res = await db.execute(
        text(
            """
            SELECT t.id AS team_id, t.name AS team_name,
                   tool.id AS tool_id, tool.name AS tool_name,
                   l.adoption_stage AS stage,
                   COUNT(DISTINCT l.resource_id) AS user_count
            FROM ai_tool_licenses l
            JOIN resources r ON r.id = l.resource_id
            JOIN teams t ON r.team_id = t.id
            JOIN ai_tools tool ON tool.id = l.tool_id
            GROUP BY t.id, t.name, tool.id, tool.name, l.adoption_stage
            """
        )
    )
    return [HeatmapCell(**dict(r._mapping)) for r in res.fetchall()]


@router.get("/trends", response_model=list[TrendPoint])
async def trends(db: AsyncSession = Depends(get_db), user: UserRole = Depends(get_current_user)):
    res = await db.execute(
        text(
            """
            SELECT u.recorded_date AS date,
                   tool.id AS tool_id, tool.name AS tool_name,
                   SUM(u.sessions) AS sessions,
                   SUM(u.active_minutes) AS active_minutes
            FROM ai_tool_usages u
            JOIN ai_tools tool ON tool.id = u.tool_id
            GROUP BY u.recorded_date, tool.id, tool.name
            ORDER BY u.recorded_date
            """
        )
    )
    return [TrendPoint(**dict(r._mapping)) for r in res.fetchall()]
