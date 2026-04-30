import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.entra import get_current_user
from app.auth.rbac import require_role, Role
from app.models.hierarchy import Account, Portfolio, SubPortfolio, Team
from app.models.resource import Resource, UserRole
from app.schemas.hierarchy import (
    PortfolioCreate, PortfolioOut, SubPortfolioCreate, SubPortfolioOut,
    TeamCreate, TeamOut, HierarchyNode,
)
from app.schemas.resource import ResourceOut
from app.utils.hierarchy_utils import get_descendant_team_ids, get_team_ids_under_portfolio
from sqlalchemy import func
from app.models.ai_adoption import AITool, AIToolLicense

router = APIRouter()


@router.get("/tree", response_model=list[HierarchyNode])
async def get_tree(db: AsyncSession = Depends(get_db), user: UserRole = Depends(get_current_user)):
    accounts = (await db.execute(select(Account))).scalars().all()
    portfolios = (await db.execute(select(Portfolio))).scalars().all()
    sub_ports = (await db.execute(select(SubPortfolio))).scalars().all()
    teams = (await db.execute(select(Team))).scalars().all()

    teams_by_parent: dict = {}
    for t in teams:
        teams_by_parent.setdefault(t.parent_team_id, []).append(t)

    def team_node(t: Team) -> HierarchyNode:
        return HierarchyNode(
            id=t.id, name=t.name, type="team",
            children=[team_node(c) for c in teams_by_parent.get(t.id, [])],
        )

    def sp_node(sp: SubPortfolio) -> HierarchyNode:
        return HierarchyNode(
            id=sp.id, name=sp.name, type="sub_portfolio",
            children=[team_node(t) for t in teams if t.sub_portfolio_id == sp.id and t.parent_team_id is None],
        )

    def p_node(p: Portfolio) -> HierarchyNode:
        children: list[HierarchyNode] = [sp_node(sp) for sp in sub_ports if sp.portfolio_id == p.id]
        children += [team_node(t) for t in teams if t.portfolio_id == p.id and t.parent_team_id is None]
        return HierarchyNode(id=p.id, name=p.name, type="portfolio", children=children)

    return [
        HierarchyNode(
            id=a.id, name=a.name, type="account",
            children=[p_node(p) for p in portfolios if p.account_id == a.id],
        )
        for a in accounts
    ]


@router.get("/portfolios", response_model=list[PortfolioOut])
async def list_portfolios(
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(get_current_user),
):
    res = await db.execute(select(Portfolio))
    return res.scalars().all()


def _top_skills(skills_strings: list[str], k: int = 5) -> list[dict]:
    counts: dict[str, int] = {}
    for s in skills_strings:
        if not s:
            continue
        for token in s.split(","):
            token = token.strip()
            if token:
                counts[token] = counts.get(token, 0) + 1
    return [
        {"skill": name, "count": count}
        for name, count in sorted(counts.items(), key=lambda x: -x[1])[:k]
    ]


@router.get("/portfolios-summary")
async def portfolios_summary(
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(get_current_user),
):
    """List of portfolios with aggregate stats — used by the Portfolios landing page."""
    portfolios = (await db.execute(select(Portfolio))).scalars().all()
    out: list[dict] = []
    for p in portfolios:
        team_ids = await get_team_ids_under_portfolio(db, str(p.id))
        if team_ids:
            res_q = await db.execute(
                select(Resource).where(
                    Resource.team_id.in_(team_ids), Resource.is_active == True
                )
            )
            resources = list(res_q.scalars().all())
        else:
            resources = []

        out.append({
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "team_count": len(team_ids),
            "resource_count": len(resources),
            "top_skills": _top_skills([r.skills or "" for r in resources], k=5),
        })
    return out


@router.get("/portfolios/{portfolio_id}/stats")
async def portfolio_stats(
    portfolio_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(get_current_user),
):
    """Full statistical breakdown for a single portfolio."""
    portfolio = await db.get(Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(404, "Portfolio not found")

    team_ids = await get_team_ids_under_portfolio(db, str(portfolio_id))
    if not team_ids:
        return {
            "id": str(portfolio_id),
            "name": portfolio.name,
            "description": portfolio.description,
            "team_count": 0,
            "resource_count": 0,
            "roles": [],
            "seniority": [],
            "skills": [],
            "ai_adoption": {"total_licenses": 0, "by_stage": {}, "by_tool": []},
        }

    resources = list((await db.execute(
        select(Resource).where(
            Resource.team_id.in_(team_ids), Resource.is_active == True
        )
    )).scalars().all())

    roles: dict[str, int] = {}
    seniority: dict[str, int] = {}
    for r in resources:
        roles[r.role] = roles.get(r.role, 0) + 1
        seniority[r.seniority] = seniority.get(r.seniority, 0) + 1

    skills = _top_skills([r.skills or "" for r in resources], k=20)

    resource_ids = [r.id for r in resources]
    if resource_ids:
        licenses = list((await db.execute(
            select(AIToolLicense).where(AIToolLicense.resource_id.in_(resource_ids))
        )).scalars().all())
    else:
        licenses = []

    by_stage: dict[str, int] = {}
    by_tool: dict[uuid.UUID, dict] = {}
    for l in licenses:
        by_stage[l.adoption_stage] = by_stage.get(l.adoption_stage, 0) + 1
        bucket = by_tool.setdefault(l.tool_id, {
            "piloting": 0, "onboarded": 0, "active": 0, "embedded": 0
        })
        bucket[l.adoption_stage] = bucket.get(l.adoption_stage, 0) + 1

    if by_tool:
        tools = list((await db.execute(
            select(AITool).where(AITool.id.in_(list(by_tool.keys())))
        )).scalars().all())
        tool_map = {t.id: t for t in tools}
        tool_breakdown = [
            {
                "tool_id": str(tid),
                "name": tool_map[tid].name if tid in tool_map else "Unknown",
                "vendor": tool_map[tid].vendor if tid in tool_map else "",
                "stages": stages,
                "total": sum(stages.values()),
            }
            for tid, stages in by_tool.items()
            if tid in tool_map
        ]
        tool_breakdown.sort(key=lambda x: -x["total"])
    else:
        tool_breakdown = []

    return {
        "id": str(portfolio_id),
        "name": portfolio.name,
        "description": portfolio.description,
        "team_count": len(team_ids),
        "resource_count": len(resources),
        "roles": [
            {"role": role, "count": count}
            for role, count in sorted(roles.items(), key=lambda x: -x[1])
        ],
        "seniority": [
            {"level": level, "count": count}
            for level, count in sorted(
                seniority.items(),
                key=lambda x: ["junior", "mid", "senior", "lead"].index(x[0]) if x[0] in ["junior", "mid", "senior", "lead"] else 99
            )
        ],
        "skills": skills,
        "ai_adoption": {
            "total_licenses": len(licenses),
            "by_stage": by_stage,
            "by_tool": tool_breakdown,
        },
    }


@router.post("/portfolios", response_model=PortfolioOut)
async def create_portfolio(
    data: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.ACCOUNT_ADMIN)),
):
    p = Portfolio(**data.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioOut)
async def get_portfolio(portfolio_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                        user: UserRole = Depends(get_current_user)):
    p = await db.get(Portfolio, portfolio_id)
    if not p:
        raise HTTPException(404, "Portfolio not found")
    return p


@router.put("/portfolios/{portfolio_id}", response_model=PortfolioOut)
async def update_portfolio(
    portfolio_id: uuid.UUID, data: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PORTFOLIO_LEAD)),
):
    p = await db.get(Portfolio, portfolio_id)
    if not p:
        raise HTTPException(404, "Portfolio not found")
    for k, v in data.model_dump().items():
        setattr(p, k, v)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/portfolios/{portfolio_id}/teams", response_model=list[TeamOut])
async def teams_under_portfolio(portfolio_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                                user: UserRole = Depends(get_current_user)):
    ids = await get_team_ids_under_portfolio(db, str(portfolio_id))
    if not ids:
        return []
    res = await db.execute(select(Team).where(Team.id.in_(ids)))
    return res.scalars().all()


@router.post("/sub-portfolios", response_model=SubPortfolioOut)
async def create_sub_portfolio(
    data: SubPortfolioCreate, db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PORTFOLIO_LEAD)),
):
    sp = SubPortfolio(**data.model_dump())
    db.add(sp)
    await db.commit()
    await db.refresh(sp)
    return sp


@router.get("/sub-portfolios/{sub_id}", response_model=SubPortfolioOut)
async def get_sub_portfolio(sub_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                            user: UserRole = Depends(get_current_user)):
    sp = await db.get(SubPortfolio, sub_id)
    if not sp:
        raise HTTPException(404, "Sub-portfolio not found")
    return sp


@router.post("/teams", response_model=TeamOut)
async def create_team(
    data: TeamCreate, db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.SUBPORTFOLIO_LEAD)),
):
    t = Team(**data.model_dump())
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t


@router.get("/teams/{team_id}", response_model=TeamOut)
async def get_team(team_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                   user: UserRole = Depends(get_current_user)):
    t = await db.get(Team, team_id)
    if not t:
        raise HTTPException(404, "Team not found")
    return t


@router.put("/teams/{team_id}", response_model=TeamOut)
async def update_team(
    team_id: uuid.UUID, data: TeamCreate, db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.TEAM_LEAD)),
):
    t = await db.get(Team, team_id)
    if not t:
        raise HTTPException(404, "Team not found")
    for k, v in data.model_dump().items():
        setattr(t, k, v)
    await db.commit()
    await db.refresh(t)
    return t


@router.get("/teams/{team_id}/members", response_model=list[ResourceOut])
async def team_members(team_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                       user: UserRole = Depends(get_current_user)):
    ids = await get_descendant_team_ids(db, str(team_id))
    if not ids:
        return []
    res = await db.execute(select(Resource).where(Resource.team_id.in_(ids), Resource.is_active == True))
    return res.scalars().all()
