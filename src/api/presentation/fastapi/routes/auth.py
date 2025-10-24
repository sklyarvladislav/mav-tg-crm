from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.api.application.schemas.user import UserSchema
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.user import User

router = APIRouter(route_class=DishkaRoute)
logger = get_logger()


@router.post("/auth")
async def authorization(
    request: UserSchema,
    session: FromDishka[AsyncSession],
    create: FromDishka[CreateGate[User, UserSchema]],
) -> UserSchema:
    async with session.begin():
        created = await create.returning()(
            UserSchema(
                user_id=request.user_id,
                username=request.username,
                number=request.number,
            )
        )

    return UserSchema(
        user_id=created.user_id,
        username=created.username,
        number=created.number,
    )
