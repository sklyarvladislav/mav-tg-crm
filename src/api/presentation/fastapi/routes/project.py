from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.api.application.schemas.project import (
    ProjectSchema,
    ProjectUpdateSchema,
)
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.project import Project
from src.api.usecases.project.delete_project import DeleteProjectUsecase
from src.api.usecases.project.get_project import GetProjectUsecase
from src.api.usecases.project.update_project import UpdateProjectUsecase

logger = get_logger()
router = APIRouter(route_class=DishkaRoute)


@router.post("")
async def create_project(
    request: ProjectSchema,
    session: FromDishka[AsyncSession],
    create: FromDishka[CreateGate[Project, ProjectSchema]],
) -> ProjectSchema:
    async with session.begin():
        created = await create.returning()(
            ProjectSchema(
                project_id=request.project_id,
                name=request.name,
                description=request.description,
                status=request.status,
                owner=request.owner,
            )
        )

    return ProjectSchema(
        project_id=created.project_id,
        name=created.name,
        description=created.description,
        status=created.status,
        owner=created.owner,
    )


@router.get("/{project_id}")
async def get_project(
    usecase: FromDishka[GetProjectUsecase],
    project_id: UUID,
) -> ProjectSchema:
    return await usecase(project_id=project_id)


@router.delete("/{project_id}")
async def delete_project(
    usecase: FromDishka[DeleteProjectUsecase],
    project_id: UUID,
) -> dict:
    await usecase(project_id=project_id)
    return {"200": "project removed"}


@router.patch("/{project_id}")
async def update_project(
    usecase: FromDishka[UpdateProjectUsecase],
    project_id: UUID,
    data: ProjectUpdateSchema,
) -> ProjectSchema:
    return await usecase(project_id=project_id, data=data)


@router.get("/owner/{owner_id}")
async def get_projects_by_owner(
    owner_id: int,
    session: FromDishka[AsyncSession],
) -> list[ProjectSchema]:
    async with session.begin():
        result = await session.execute(
            select(Project).where(Project.owner == owner_id)
        )
        projects = result.scalars().all()

    return [
        ProjectSchema(
            project_id=p.project_id,
            name=p.name,
            description=p.description,
            status=p.status,
            owner=p.owner,
        )
        for p in projects
    ]
