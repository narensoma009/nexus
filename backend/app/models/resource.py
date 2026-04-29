import uuid
from sqlalchemy import String, ForeignKey, Boolean, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id"))
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[str] = mapped_column(String(255))
    seniority: Mapped[str] = mapped_column(String(50))
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    team: Mapped["Team"] = relationship(back_populates="members")
    assignments: Mapped[list["ResourceAssignment"]] = relationship(back_populates="resource")
    tool_usages: Mapped[list["AIToolUsage"]] = relationship(back_populates="resource")


class UserRole(Base):
    """Maps Entra ID user to platform role + hierarchy scope."""
    __tablename__ = "user_roles"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    entra_oid: Mapped[str] = mapped_column(String(255), unique=True)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("resources.id"), nullable=True)
    role: Mapped[str] = mapped_column(String(50))
    scope_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
