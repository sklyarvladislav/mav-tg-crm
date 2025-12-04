from dataclasses import dataclass
from uuid import UUID

from src.api.application.schemas.board import BoardSchema
from src.api.infra.database.core.board.gates import GetBoardGate


@dataclass(slots=True, frozen=True, kw_only=True)
class GetBoardUsecase:
    get_board: GetBoardGate

    async def __call__(self, board_id: UUID) -> BoardSchema:
        board: BoardSchema = await self.get_board(board_id=board_id)

        return BoardSchema(
            board_id=board.board_id,
            project_id=board.project_id,
            name=board.name,
            position=board.position,
            number_tasks=board.number_tasks,
        )
