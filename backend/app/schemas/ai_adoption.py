import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AIToolBase(BaseModel):
    name: str
    vendor: str
    category: str
    rollout_date: datetime | None = None
    target_user_count: int | None = None


class AIToolCreate(AIToolBase):
    pass


class AIToolOut(AIToolBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class AIToolLicenseBase(BaseModel):
    tool_id: uuid.UUID
    resource_id: uuid.UUID
    adoption_stage: str = "piloting"


class AIToolLicenseCreate(AIToolLicenseBase):
    pass


class AIToolLicenseUpdate(BaseModel):
    adoption_stage: str


class AIToolLicenseOut(AIToolLicenseBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    assigned_date: datetime


class AIToolUsageCreate(BaseModel):
    tool_id: uuid.UUID
    resource_id: uuid.UUID
    recorded_date: datetime
    sessions: int = 0
    active_minutes: int = 0
    source: str = "manual"


class AIToolUsageOut(AIToolUsageCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class AdoptionSummary(BaseModel):
    total_resources: int
    active_users: int
    active_pct: float
    tools_tracked: int
    avg_stage_score: float


class HeatmapCell(BaseModel):
    team_id: uuid.UUID
    team_name: str
    tool_id: uuid.UUID
    tool_name: str
    stage: str
    user_count: int


class TrendPoint(BaseModel):
    date: datetime
    tool_id: uuid.UUID
    tool_name: str
    sessions: int
    active_minutes: int
