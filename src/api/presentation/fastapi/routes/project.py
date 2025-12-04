from dataclasses import asdict
from uuid import UUID, uuid4

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.application.schemas.participant import ParticipantSchema
from src.api.application.schemas.project import (
    ProjectSchema,
    ProjectUpdateSchema,
)
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.project import Project, ProjectParticipant

router = APIRouter(route_class=DishkaRoute)


@router.post("")
async def create_project(
    request: ProjectSchema,
    session: FromDishka[AsyncSession],
    create: FromDishka[CreateGate[Project, ProjectSchema]],
    create_participant: FromDishka[
        CreateGate[ProjectParticipant, ParticipantSchema]
    ],
    user_id: int,
) -> ProjectSchema:
    async with session.begin():
        created_project = await create.returning()(
            ProjectSchema(
                project_id=uuid4(),
                name=request.name,
                description=request.description,
                status=request.status,
            )
        )

        await create_participant(
            ParticipantSchema(
                project_id=created_project.project_id,
                user_id=user_id,
                role="OWNER",
            )
        )

    return ProjectSchema(
        project_id=created_project.project_id,
        name=created_project.name,
        description=created_project.description,
        status=created_project.status,
    )


@router.get("/{project_id}")
async def get_project(
    project_id: UUID, session: FromDishka[AsyncSession]
) -> ProjectSchema:
    stmt = select(Project).where(Project.project_id == project_id)
    result = await session.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectSchema(
        project_id=project.project_id,
        name=project.name,
        description=project.description,
        status=project.status,
    )


@router.get("/user/{user_id}")
async def get_projects_by_user(
    user_id: int, session: FromDishka[AsyncSession]
) -> list[ProjectSchema]:
    stmt = (
        select(Project)
        .join(
            ProjectParticipant,
            Project.project_id == ProjectParticipant.project_id,
        )
        .where(ProjectParticipant.user_id == user_id)
    )
    result = await session.execute(stmt)
    projects = result.scalars().all()

    return [
        ProjectSchema(
            project_id=p.project_id,
            name=p.name,
            description=p.description,
            status=p.status,
        )
        for p in projects
    ]


@router.delete("/{project_id}")
async def delete_project(
    project_id: UUID, session: FromDishka[AsyncSession]
) -> dict:
    stmt = select(Project).where(Project.project_id == project_id)
    result = await session.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await session.delete(project)
    await session.commit()
    return {"200": "project removed"}


@router.patch("/{project_id}")
async def update_project(
    project_id: UUID,
    data: ProjectUpdateSchema,
    session: FromDishka[AsyncSession],
) -> ProjectSchema:
    stmt = select(Project).where(Project.project_id == project_id)
    result = await session.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in asdict(data).items():
        if value is not None:
            setattr(project, field, value)

    await session.commit()
    return ProjectSchema(
        project_id=project.project_id,
        name=project.name,
        description=project.description,
        status=project.status,
    )
