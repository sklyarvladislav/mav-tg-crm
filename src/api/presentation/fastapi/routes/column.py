from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.api.application.schemas.board import (
    BoardColumnSchema,
    BoardColumnUpdateSchema,
)
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.board import BoardColumn
from src.api.usecases.column import (
    DeleteBoardColumnUsecase,
    GetBoardColumnUsecase,
    UpdateBoardColumnUsecase,
)

logger = get_logger()
router = APIRouter(route_class=DishkaRoute)


@router.post("")
async def create_column(
    request: BoardColumnSchema,
    session: FromDishka[AsyncSession],
    create: FromDishka[CreateGate[BoardColumn, BoardColumnSchema]],
) -> BoardColumnSchema:
    async with session.begin():
        created = await create.returning()(
            BoardColumnSchema(
                column_id=request.column_id,
                board_id=request.board_id,
                name=request.name,
                position=request.position,
            )
        )

    return BoardColumnSchema(
        column_id=created.column_id,
        board_id=created.board_id,
        name=created.name,
        position=created.position,
    )


@router.get("/{column_id}")
async def get_column(
    usecase: FromDishka[GetBoardColumnUsecase],
    column_id: UUID,
) -> BoardColumnSchema:
    return await usecase(column_id=column_id)


@router.delete("/{column_id}")
async def delete_column(
    usecase: FromDishka[DeleteBoardColumnUsecase],
    column_id: UUID,
) -> dict:
    await usecase(column_id=column_id)
    return {"200": "column removed"}


@router.patch("/{column_id}")
async def update_column(
    usecase: FromDishka[UpdateBoardColumnUsecase],
    column_id: UUID,
    data: BoardColumnUpdateSchema,
) -> BoardColumnSchema:
    return await usecase(column_id=column_id, data=data)
