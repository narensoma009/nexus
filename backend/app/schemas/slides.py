import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PlaceholderInfo(BaseModel):
    token: str
    type: str  # data | table | chart | ai | auto
    description: str | None = None


class PPTTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    tags: str | None
    slide_count: int
    placeholder_map: str
    uploaded_by: str
    uploaded_at: datetime
    last_used_at: datetime | None


class GenerateSlidesRequest(BaseModel):
    template_id: uuid.UUID
    program_id: uuid.UUID | None = None
    period: str | None = None
    scope: dict | None = None


class JobStatus(BaseModel):
    job_id: str
    status: str  # queued | running | completed | failed
    download_url: str | None = None
    error: str | None = None
