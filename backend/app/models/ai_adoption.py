import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AITool(Base):
    __tablename__ = "ai_tools"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    vendor: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    rollout_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    target_user_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    licenses: Mapped[list["AIToolLicense"]] = relationship(back_populates="tool")


class AIToolLicense(Base):
    __tablename__ = "ai_tool_licenses"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_tools.id"))
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resources.id"))
    assigned_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    adoption_stage: Mapped[str] = mapped_column(String(50), default="piloting")
    tool: Mapped["AITool"] = relationship(back_populates="licenses")


class AIToolUsage(Base):
    __tablename__ = "ai_tool_usages"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_tools.id"))
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resources.id"))
    recorded_date: Mapped[datetime] = mapped_column(DateTime)
    sessions: Mapped[int] = mapped_column(Integer, default=0)
    active_minutes: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(50), default="manual")
    resource: Mapped["Resource"] = relationship(back_populates="tool_usages")
