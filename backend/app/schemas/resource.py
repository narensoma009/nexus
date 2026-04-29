import uuid
from pydantic import BaseModel, ConfigDict, EmailStr


class ResourceBase(BaseModel):
    name: str
    email: EmailStr
    role: str
    seniority: str
    skills: str | None = None
    team_id: uuid.UUID
    is_active: bool = True


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    seniority: str | None = None
    skills: str | None = None
    team_id: uuid.UUID | None = None
    is_active: bool | None = None


class ResourceOut(ResourceBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class UserRoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    entra_oid: str
    resource_id: uuid.UUID | None
    role: str
    scope_id: uuid.UUID | None
