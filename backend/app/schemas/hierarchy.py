import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AccountBase(BaseModel):
    name: str


class AccountCreate(AccountBase):
    pass


class AccountOut(AccountBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime


class PortfolioBase(BaseModel):
    name: str
    description: str | None = None


class PortfolioCreate(PortfolioBase):
    account_id: uuid.UUID


class PortfolioOut(PortfolioBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    account_id: uuid.UUID


class SubPortfolioBase(BaseModel):
    name: str
    description: str | None = None


class SubPortfolioCreate(SubPortfolioBase):
    portfolio_id: uuid.UUID


class SubPortfolioOut(SubPortfolioBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    portfolio_id: uuid.UUID


class TeamBase(BaseModel):
    name: str
    portfolio_id: uuid.UUID | None = None
    sub_portfolio_id: uuid.UUID | None = None
    parent_team_id: uuid.UUID | None = None


class TeamCreate(TeamBase):
    pass


class TeamOut(TeamBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class HierarchyNode(BaseModel):
    id: uuid.UUID
    name: str
    type: str  # account | portfolio | sub_portfolio | team
    children: list["HierarchyNode"] = []


HierarchyNode.model_rebuild()
