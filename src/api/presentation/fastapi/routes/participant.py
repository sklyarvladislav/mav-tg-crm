from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.application.schemas.participant import (
    ParticipantSchema,
    ParticipantUpdateSchema,
)
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.project import ProjectParticipant

router = APIRouter(route_class=DishkaRoute)


@router.post("")
async def create_participant(
    request: ParticipantSchema,
    session: FromDishka[AsyncSession],
    create: FromDishka[CreateGate[ProjectParticipant, ParticipantSchema]],
) -> ParticipantSchema:
    async with session.begin():
        created = await create.returning()(request)

    return ParticipantSchema(
        project_id=created.project_id,
        user_id=created.user_id,
        role=created.role,
    )


@router.get("/{user_id}")
async def get_participant(
    user_id: int, session: FromDishka[AsyncSession]
) -> list[ParticipantSchema]:
    stmt = select(ProjectParticipant).where(
        ProjectParticipant.user_id == user_id
    )
    result = await session.execute(stmt)
    participants = result.scalars().all()

    return [
        ParticipantSchema(
            project_id=p.project_id, user_id=p.user_id, role=p.role
        )
        for p in participants
    ]


@router.get("/{project_id}/participants")
async def get_project_participants(
    project_id: UUID, session: FromDishka[AsyncSession]
) -> list[ParticipantSchema]:
    stmt = select(ProjectParticipant).where(
        ProjectParticipant.project_id == project_id
    )
    result = await session.execute(stmt)
    participants = result.scalars().all()
    return [
        ParticipantSchema(
            project_id=p.project_id, user_id=p.user_id, role=p.role
        )
        for p in participants
    ]


@router.delete("/{participant_id}")
async def delete_participant(
    user_id: int, project_id: UUID, session: FromDishka[AsyncSession]
) -> dict:
    stmt = select(ProjectParticipant).where(
        ProjectParticipant.project_id == project_id,
        ProjectParticipant.user_id == user_id,
    )
    result = await session.execute(stmt)
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    await session.delete(participant)
    await session.commit()
    return {"200": "participant removed"}


@router.patch("/{participant_id}")
async def update_participant(
    participant_id: UUID,
    data: ParticipantUpdateSchema,
    session: FromDishka[AsyncSession],
) -> ParticipantSchema:
    stmt = select(ProjectParticipant).where(
        ProjectParticipant.user_id == participant_id
    )
    result = await session.execute(stmt)
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(participant, field, value)

    await session.commit()
    return ParticipantSchema(
        project_id=participant.project_id,
        user_id=participant.user_id,
        role=participant.role,
    )
