from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.api.application.schemas.task import (
    TaskSchema,
    TaskUpdateSchema,
)
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.task import Task
from src.api.usecases.task.delete_task import DeleteTaskUsecase
from src.api.usecases.task.get_task import GetTaskUsecase
from src.api.usecases.task.update_task import UpdateTaskUsecase

logger = get_logger()
router = APIRouter(route_class=DishkaRoute)


@router.post("")
async def create_task(
    request: TaskSchema,
    session: FromDishka[AsyncSession],
    create: FromDishka[CreateGate[Task, TaskSchema]],
) -> TaskSchema:
    async with session.begin():
        created = await create.returning()(
            TaskSchema(
                task_id=request.task_id,
                name=request.name,
                text=request.text,
                document_id=request.document_id,
                user_id=request.user_id,
                project_id=request.project_id,
                board_id=request.board_id,
                column_id=request.column_id,
                deadline=request.deadline,
                status=request.status,
                priority=request.priority,
                number=request.number,
            )
        )

    return TaskSchema(
        task_id=created.task_id,
        name=created.name,
        text=created.text,
        document_id=created.document_id,
        user_id=created.user_id,
        project_id=created.project_id,
        board_id=created.board_id,
        column_id=created.column_id,
        deadline=created.deadline,
        status=created.status,
        priority=created.priority,
        number=created.number,
    )


@router.get("/{task_id}")
async def get_task(
    usecase: FromDishka[GetTaskUsecase],
    task_id: UUID,
) -> TaskSchema:
    return await usecase(task_id=task_id)


@router.get("/{project_id}/tasks")
async def get_project_tasks(
    project_id: UUID,
    session: FromDishka[AsyncSession],
) -> list[TaskSchema]:
    async with session.begin():
        result = await session.execute(
            select(Task).where(Task.project_id == project_id)
        )
        tasks = result.scalars().all()

    return [
        TaskSchema(
            task_id=task.task_id,
            name=task.name,
            text=task.text,
            document_id=task.document_id,
            user_id=task.user_id,
            project_id=task.project_id,
            board_id=task.board_id,
            column_id=task.column_id,
            number=task.number,
            status=task.status,
            priority=task.priority,
        )
        for task in tasks
    ]


@router.delete("/{task_id}")
async def delete_task(
    usecase: FromDishka[DeleteTaskUsecase],
    task_id: UUID,
) -> dict:
    await usecase(task_id=task_id)
    return {"200": "task removed"}


@router.patch("/{task_id}")
async def update_task(
    usecase: FromDishka[UpdateTaskUsecase],
    task_id: UUID,
    data: TaskUpdateSchema,
) -> TaskSchema:
    return await usecase(task_id=task_id, data=data)
