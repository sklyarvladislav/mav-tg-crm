from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.api.application.schemas.user import UserSchema
from src.api.infra.database.tables.user import User

router = APIRouter(route_class=DishkaRoute, tags=["User"])
logger = get_logger()


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    session: FromDishka[AsyncSession],
) -> UserSchema:
    async with session.begin():
        user = await session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserSchema(
        user_id=user.user_id,
        short_name=user.short_name,
        username=user.username,
        number=user.number,
    )


@router.patch("/{user_id}")
async def update_user(
    user_id: int, request: UserSchema, session: FromDishka[AsyncSession]
) -> UserSchema:
    async with session.begin():
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if request.username:
            user.username = request.username
        if request.number:
            user.number = request.number

        await session.commit()

    return UserSchema(
        user_id=user.user_id,
        short_name=user.short_name,
        username=user.username,
        number=user.number,
    )


@router.delete("/{user_id}")
async def delete_user(user_id: int, session: FromDishka[AsyncSession]) -> dict:
    async with session.begin():
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404)

        await session.delete(user)
        await session.commit()

    return {"message": "User deleted"}
