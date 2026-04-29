import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Program(Base):
    __tablename__ = "programs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="on_track")
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    projects: Mapped[list["Project"]] = relationship(back_populates="program")


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("programs.id"))
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="on_track")
    program: Mapped["Program"] = relationship(back_populates="projects")
    workstreams: Mapped[list["Workstream"]] = relationship(back_populates="project")


class Workstream(Base):
    __tablename__ = "workstreams"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="on_track")
    project: Mapped["Project"] = relationship(back_populates="workstreams")
    assignments: Mapped[list["ResourceAssignment"]] = relationship(back_populates="workstream")


class ResourceAssignment(Base):
    __tablename__ = "resource_assignments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resources.id"))
    workstream_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workstreams.id"))
    role: Mapped[str] = mapped_column(String(255))
    allocation_pct: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resource: Mapped["Resource"] = relationship(back_populates="assignments")
    workstream: Mapped["Workstream"] = relationship(back_populates="assignments")
