import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    portfolios: Mapped[list["Portfolio"]] = relationship(back_populates="account")


class Portfolio(Base):
    __tablename__ = "portfolios"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    account: Mapped["Account"] = relationship(back_populates="portfolios")
    sub_portfolios: Mapped[list["SubPortfolio"]] = relationship(back_populates="portfolio")
    teams: Mapped[list["Team"]] = relationship(
        back_populates="portfolio",
        primaryjoin="and_(Team.portfolio_id == Portfolio.id, Team.parent_team_id == None)",
        foreign_keys="[Team.portfolio_id]",
    )


class SubPortfolio(Base):
    __tablename__ = "sub_portfolios"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portfolios.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    portfolio: Mapped["Portfolio"] = relationship(back_populates="sub_portfolios")
    teams: Mapped[list["Team"]] = relationship(back_populates="sub_portfolio")


class Team(Base):
    """Recursive — a team can have a parent team (sub-teams)."""
    __tablename__ = "teams"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    portfolio_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("portfolios.id"), nullable=True)
    sub_portfolio_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sub_portfolios.id"), nullable=True)
    parent_team_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    portfolio: Mapped["Portfolio | None"] = relationship(back_populates="teams", foreign_keys=[portfolio_id])
    sub_portfolio: Mapped["SubPortfolio | None"] = relationship(back_populates="teams")
    parent_team: Mapped["Team | None"] = relationship(back_populates="sub_teams", remote_side="Team.id")
    sub_teams: Mapped[list["Team"]] = relationship(back_populates="parent_team")
    members: Mapped[list["Resource"]] = relationship(back_populates="team")
