from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.api.application.schemas.board import (
    BoardSchema,
    BoardUpdateSchema,
)
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.board import Board
from src.api.usecases.board import (
    DeleteBoardUsecase,
    GetBoardUsecase,
    UpdateBoardUsecase,
)

logger = get_logger()
router = APIRouter(route_class=DishkaRoute)


@router.post("")
async def create_board(
    request: BoardSchema,
    session: FromDishka[AsyncSession],
    create: FromDishka[CreateGate[Board, BoardSchema]],
) -> BoardSchema:
    async with session.begin():
        created = await create.returning()(
            BoardSchema(
                board_id=request.board_id,
                project_id=request.project_id,
                name=request.name,
                position=request.position,
                number_tasks=request.number_tasks,
            )
        )

    return BoardSchema(
        board_id=created.board_id,
        project_id=created.project_id,
        name=created.name,
        position=created.position,
        number_tasks=created.number_tasks,
    )


@router.get("/{board_id}")
async def get_board(
    usecase: FromDishka[GetBoardUsecase],
    board_id: UUID,
) -> BoardSchema:
    return await usecase(board_id=board_id)


@router.get("/{project_id}/boards")
async def get_project_documents(
    project_id: UUID,
    session: FromDishka[AsyncSession],
) -> list[BoardSchema]:
    async with session.begin():
        result = await session.execute(
            select(Board).where(Board.project_id == project_id)
        )
        boards = result.scalars().all()

    return [
        BoardSchema(
            board_id=board.board_id,
            project_id=board.project_id,
            name=board.name,
            position=board.position,
            number_tasks=board.number_tasks,
        )
        for board in boards
    ]


@router.delete("/{board_id}")
async def delete_board(
    usecase: FromDishka[DeleteBoardUsecase],
    board_id: UUID,
) -> dict:
    await usecase(board_id=board_id)
    return {"200": "board removed"}


@router.patch("/{board_id}")
async def update_board(
    usecase: FromDishka[UpdateBoardUsecase],
    board_id: UUID,
    data: BoardUpdateSchema,
) -> BoardSchema:
    return await usecase(board_id=board_id, data=data)
