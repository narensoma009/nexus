import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ProgramBase(BaseModel):
    name: str
    description: str | None = None
    status: str = "on_track"
    start_date: datetime | None = None
    end_date: datetime | None = None


class ProgramCreate(ProgramBase):
    account_id: uuid.UUID


class ProgramUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class ProgramOut(ProgramBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    account_id: uuid.UUID


class ProjectBase(BaseModel):
    name: str
    status: str = "on_track"


class ProjectCreate(ProjectBase):
    program_id: uuid.UUID


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    program_id: uuid.UUID


class WorkstreamBase(BaseModel):
    name: str
    status: str = "on_track"


class WorkstreamCreate(WorkstreamBase):
    project_id: uuid.UUID


class WorkstreamOut(WorkstreamBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    project_id: uuid.UUID


class AssignmentBase(BaseModel):
    resource_id: uuid.UUID
    workstream_id: uuid.UUID
    role: str
    allocation_pct: int
    start_date: datetime | None = None
    end_date: datetime | None = None


class AssignmentCreate(AssignmentBase):
    pass


class AssignmentUpdate(BaseModel):
    role: str | None = None
    allocation_pct: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class AssignmentOut(AssignmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class PortfolioSpreadEntry(BaseModel):
    portfolio_id: uuid.UUID
    portfolio_name: str
    team_count: int
    resource_count: int
