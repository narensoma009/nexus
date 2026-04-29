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
    user: UserRole = Depends(require_role(Role.ACCOUNT_ADMIN)),
):
    res = await db.execute(select(Portfolio))
    return res.scalars().all()


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
