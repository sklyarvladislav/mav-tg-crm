from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.api.application.schemas.participant import (
    ParticipantSchema,
    ParticipantUpdateSchema,
)
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.project import ProjectParticipant
from src.api.usecases.participant import (
    ChangeRoleParticipantUsecase,
    DeleteParticipantUsecase,
    GetParticipantUsecase,
)

logger = get_logger()
router = APIRouter(route_class=DishkaRoute)


@router.post("")
async def create_participant(
    request: ParticipantSchema,
    session: FromDishka[AsyncSession],
    create: FromDishka[CreateGate[ProjectParticipant, ParticipantSchema]],
) -> ParticipantSchema:
    async with session.begin():
        created = await create.returning()(
            ParticipantSchema(
                project_id=request.project_id,
                user_id=request.user_id,
                role=request.role,
            )
        )

    return ParticipantSchema(
        project_id=created.project_id,
        user_id=created.user_id,
        role=created.role,
    )


@router.get("/{participant_id}")
async def get_participant(
    usecase: FromDishka[GetParticipantUsecase],
    user_id: int,
) -> ParticipantSchema:
    return await usecase(user_id=user_id)


@router.get("/{project_id}/participants")
async def get_project_participants(
    project_id: UUID,
    session: FromDishka[AsyncSession],
) -> list[ParticipantSchema]:
    stmt = select(ProjectParticipant).where(
        ProjectParticipant.project_id == project_id
    )

    result = await session.execute(stmt)
    participants = result.scalars().all()

    return [
        ParticipantSchema(
            project_id=p.project_id,
            user_id=p.user_id,
            role=p.role,
        )
        for p in participants
    ]


@router.delete("/{participant_id}")
async def delete_participant(
    usecase: FromDishka[DeleteParticipantUsecase],
    user_id: int,
    project_id: UUID,
) -> dict:
    await usecase(user_id=user_id, project_id=project_id)
    return {"200": "participant removed"}


@router.patch("/{participant_id}")
async def update_participant(
    usecase: FromDishka[ChangeRoleParticipantUsecase],
    participant_id: UUID,
    data: ParticipantUpdateSchema,
) -> ParticipantSchema:
    return await usecase(participant_id=participant_id, data=data)
