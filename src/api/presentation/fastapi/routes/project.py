from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.api.application.schemas.project import ProjectSchema
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.project import Project
from src.api.usecases.project.delete_project import DeleteProjectUsecase
from src.api.usecases.project.get_project import GetProjectUsecase

logger = get_logger()
router = APIRouter(route_class=DishkaRoute)


@router.post("", tags=["Project"])
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


@router.get("", tags=["Project"])
async def get_project(
    usecase: FromDishka[GetProjectUsecase],
    project_id: UUID,
) -> ProjectSchema:
    return await usecase(project_id=project_id)


@router.delete("", tags=["Project"])
async def delete_project(
    usecase: FromDishka[DeleteProjectUsecase],
    project_id: UUID,
) -> dict:
    await usecase(project_id=project_id)
    return {"200": "project removed"}


@router.put("", tags=["Project"])
async def update_project() -> None:
    pass
