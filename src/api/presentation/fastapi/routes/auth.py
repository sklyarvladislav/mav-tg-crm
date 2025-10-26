from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.api.application.schemas.user import UserSchema
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.user import User

router = APIRouter(route_class=DishkaRoute)
logger = get_logger()


@router.post("", tags=["Authorization"])
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

@router.get("/user/{user_id}", tags=["Authorization"])
async def get_user(
    user_id: int,
    session: FromDishka[AsyncSession],
) -> UserSchema:
    async with session.begin():
        user = await session.get(User, user_id)

    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    return UserSchema(
        user_id=user.user_id,
        username=user.username,
        number=user.number,
    )