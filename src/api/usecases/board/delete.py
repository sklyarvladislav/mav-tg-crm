from dataclasses import dataclass
from uuid import UUID

from src.api.infra.database.core.board.gates import (
    DeleteBoardGate,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class DeleteBoardUsecase:
    delete_board: DeleteBoardGate

    async def __call__(self, board_id: UUID) -> bool:
        return await self.delete_board(board_id=board_id)
