import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.entra import get_current_user
from app.auth.rbac import require_role, Role
from app.models.resource import Resource, UserRole
from app.models.program import ResourceAssignment
from app.models.ai_adoption import AIToolUsage
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceOut
from app.schemas.program import AssignmentOut
from app.schemas.ai_adoption import AIToolUsageOut

router = APIRouter()


@router.get("", response_model=list[ResourceOut])
async def list_resources(
    team_id: uuid.UUID | None = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(get_current_user),
):
    q = select(Resource)
    if team_id:
        q = q.where(Resource.team_id == team_id)
    q = q.offset((page - 1) * page_size).limit(page_size)
    res = await db.execute(q)
    return res.scalars().all()


@router.get("/{resource_id}", response_model=ResourceOut)
async def get_resource(resource_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                       user: UserRole = Depends(get_current_user)):
    r = await db.get(Resource, resource_id)
    if not r:
        raise HTTPException(404, "Resource not found")
    return r


@router.post("", response_model=ResourceOut)
async def create_resource(
    data: ResourceCreate, db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.TEAM_LEAD)),
):
    r = Resource(**data.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@router.put("/{resource_id}", response_model=ResourceOut)
async def update_resource(
    resource_id: uuid.UUID, data: ResourceUpdate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.TEAM_LEAD)),
):
    r = await db.get(Resource, resource_id)
    if not r:
        raise HTTPException(404, "Resource not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.commit()
    await db.refresh(r)
    return r


@router.get("/{resource_id}/assignments", response_model=list[AssignmentOut])
async def resource_assignments(resource_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                               user: UserRole = Depends(get_current_user)):
    res = await db.execute(select(ResourceAssignment).where(ResourceAssignment.resource_id == resource_id))
    return res.scalars().all()


@router.get("/{resource_id}/ai-usage", response_model=list[AIToolUsageOut])
async def resource_ai_usage(resource_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                            user: UserRole = Depends(get_current_user)):
    res = await db.execute(select(AIToolUsage).where(AIToolUsage.resource_id == resource_id))
    return res.scalars().all()


@router.post("/bulk-import")
async def bulk_import(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PORTFOLIO_LEAD)),
):
    from app.services.ingestion_service import import_roster_csv
    contents = await file.read()
    try:
        return await import_roster_csv(contents, db)
    except ValueError as e:
        raise HTTPException(400, str(e))
