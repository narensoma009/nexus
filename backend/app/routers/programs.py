import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.entra import get_current_user
from app.auth.rbac import require_role, Role
from app.models.program import Program, Project, Workstream, ResourceAssignment
from app.models.resource import Resource, UserRole
from app.schemas.program import (
    ProgramCreate, ProgramUpdate, ProgramOut,
    ProjectCreate, ProjectOut,
    WorkstreamCreate, WorkstreamOut,
    AssignmentCreate, AssignmentUpdate, AssignmentOut,
    PortfolioSpreadEntry,
)
from app.schemas.resource import ResourceOut

router = APIRouter()


@router.get("/programs", response_model=list[ProgramOut])
async def list_programs(db: AsyncSession = Depends(get_db), user: UserRole = Depends(get_current_user)):
    res = await db.execute(select(Program))
    return res.scalars().all()


@router.post("/programs", response_model=ProgramOut)
async def create_program(
    data: ProgramCreate, db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PM)),
):
    p = Program(**data.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/programs/{program_id}", response_model=ProgramOut)
async def get_program(program_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                      user: UserRole = Depends(get_current_user)):
    p = await db.get(Program, program_id)
    if not p:
        raise HTTPException(404, "Program not found")
    return p


@router.put("/programs/{program_id}", response_model=ProgramOut)
async def update_program(
    program_id: uuid.UUID, data: ProgramUpdate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PM)),
):
    p = await db.get(Program, program_id)
    if not p:
        raise HTTPException(404, "Program not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/programs/{program_id}/portfolio-spread", response_model=list[PortfolioSpreadEntry])
async def portfolio_spread(program_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                           user: UserRole = Depends(get_current_user)):
    result = await db.execute(
        text(
            """
            SELECT p.id AS portfolio_id, p.name AS portfolio_name,
                   COUNT(DISTINCT t.id) AS team_count,
                   COUNT(DISTINCT r.id) AS resource_count
            FROM programs prog
            JOIN projects proj ON proj.program_id = prog.id
            JOIN workstreams ws ON ws.project_id = proj.id
            JOIN resource_assignments ra ON ra.workstream_id = ws.id
            JOIN resources r ON r.id = ra.resource_id
            JOIN teams t ON r.team_id = t.id
            LEFT JOIN sub_portfolios sp ON t.sub_portfolio_id = sp.id
            JOIN portfolios p ON p.id = COALESCE(t.portfolio_id, sp.portfolio_id)
            WHERE prog.id = :pid
            GROUP BY p.id, p.name
            ORDER BY resource_count DESC
            """
        ),
        {"pid": str(program_id)},
    )
    return [PortfolioSpreadEntry(**dict(r._mapping)) for r in result.fetchall()]


@router.get("/programs/{program_id}/workstreams", response_model=list[WorkstreamOut])
async def program_workstreams(program_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                              user: UserRole = Depends(get_current_user)):
    res = await db.execute(
        select(Workstream).join(Project).where(Project.program_id == program_id)
    )
    return res.scalars().all()


@router.get("/programs/{program_id}/resources", response_model=list[ResourceOut])
async def program_resources(program_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                            user: UserRole = Depends(get_current_user)):
    res = await db.execute(
        select(Resource).distinct()
        .join(ResourceAssignment, ResourceAssignment.resource_id == Resource.id)
        .join(Workstream, Workstream.id == ResourceAssignment.workstream_id)
        .join(Project, Project.id == Workstream.project_id)
        .where(Project.program_id == program_id)
    )
    return res.scalars().all()


@router.post("/programs/{program_id}/projects", response_model=ProjectOut)
async def create_project(
    program_id: uuid.UUID, data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PM)),
):
    p = Project(name=data.name, status=data.status, program_id=program_id)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                      user: UserRole = Depends(get_current_user)):
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(404, "Project not found")
    return p


@router.post("/projects/{project_id}/workstreams", response_model=WorkstreamOut)
async def create_workstream(
    project_id: uuid.UUID, data: WorkstreamCreate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PM)),
):
    w = Workstream(name=data.name, status=data.status, project_id=project_id)
    db.add(w)
    await db.commit()
    await db.refresh(w)
    return w


@router.get("/workstreams/{workstream_id}", response_model=WorkstreamOut)
async def get_workstream(workstream_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                         user: UserRole = Depends(get_current_user)):
    w = await db.get(Workstream, workstream_id)
    if not w:
        raise HTTPException(404, "Workstream not found")
    return w


@router.get("/workstreams/{workstream_id}/assignments", response_model=list[AssignmentOut])
async def workstream_assignments(workstream_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                                 user: UserRole = Depends(get_current_user)):
    res = await db.execute(select(ResourceAssignment).where(ResourceAssignment.workstream_id == workstream_id))
    return res.scalars().all()


@router.post("/workstreams/{workstream_id}/assignments", response_model=AssignmentOut)
async def create_assignment(
    workstream_id: uuid.UUID, data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PM)),
):
    payload = data.model_dump()
    payload["workstream_id"] = workstream_id
    a = ResourceAssignment(**payload)
    db.add(a)
    await db.commit()
    await db.refresh(a)
    return a


@router.put("/assignments/{assignment_id}", response_model=AssignmentOut)
async def update_assignment(
    assignment_id: uuid.UUID, data: AssignmentUpdate,
    db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PM)),
):
    a = await db.get(ResourceAssignment, assignment_id)
    if not a:
        raise HTTPException(404, "Assignment not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    await db.commit()
    await db.refresh(a)
    return a


@router.delete("/assignments/{assignment_id}")
async def delete_assignment(
    assignment_id: uuid.UUID, db: AsyncSession = Depends(get_db),
    user: UserRole = Depends(require_role(Role.PM)),
):
    a = await db.get(ResourceAssignment, assignment_id)
    if not a:
        raise HTTPException(404, "Assignment not found")
    await db.delete(a)
    await db.commit()
    return {"deleted": True}
