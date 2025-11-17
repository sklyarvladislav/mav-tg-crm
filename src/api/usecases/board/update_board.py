from dataclasses import asdict, dataclass
from uuid import UUID

from src.api.application.schemas.board import (
    BoardSchema,
    BoardUpdateSchema,
)
from src.api.infra.database.core.board.gates.update import (
    UpdateBoardGate,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateBoardUsecase:
    update_board: UpdateBoardGate

    async def __call__(
        self, board_id: UUID, data: BoardUpdateSchema
    ) -> BoardSchema:
        update_data = {k: v for k, v in asdict(data).items() if v is not None}
        return await self.update_board(board_id=board_id, data=update_data)
