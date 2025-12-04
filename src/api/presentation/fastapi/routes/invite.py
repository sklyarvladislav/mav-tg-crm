import uuid

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.application.schemas.invite import InviteSchema
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.project import (
    ProjectInvite,
    ProjectParticipant,
)

router = APIRouter(route_class=DishkaRoute)


@router.post("/{project_id}/invite")
async def create_invite(
    session: FromDishka[AsyncSession],
    create: FromDishka[CreateGate[ProjectInvite, InviteSchema]],
    project_id: uuid.UUID,
) -> InviteSchema:
    token = uuid.uuid4()

    # создаём DTO
    invite_data = InviteSchema(
        token=token,
        project_id=project_id,
    )

    async with session.begin():
        created = await create.returning()(invite_data)

    return InviteSchema(
        token=created.token,
        project_id=created.project_id,
        created_at=created.created_at,
        expires_at=created.expires_at,
    )


@router.post("/invite/{token}/accept")
async def accept_invite(
    token: uuid.UUID, data: dict, session: FromDishka[AsyncSession]
) -> None:
    user_id = data["user_id"]

    # выбираем приглашение
    stmt = select(ProjectInvite).where(ProjectInvite.token == token)
    result = await session.execute(stmt)
    invite = result.scalar_one_or_none()

    if invite is None:
        raise HTTPException(status_code=404, detail="Invite not found")

    # добавляем участника проекта
    participant = ProjectParticipant(
        project_id=invite.project_id,
        user_id=user_id,
        role="USER",
    )

    session.add(participant)
    await session.commit()

    return {"status": "ok"}
