from dataclasses import dataclass
from uuid import UUID

from src.api.application.schemas.board import BoardColumnSchema
from src.api.infra.database.core.column.gates.get import GetBoardColumnGate


@dataclass(slots=True, frozen=True, kw_only=True)
class GetBoardColumnUsecase:
    get_column: GetBoardColumnGate

    async def __call__(self, column_id: UUID) -> BoardColumnSchema:
        column: BoardColumnSchema = await self.get_column(column_id=column_id)

        return BoardColumnSchema(
            column_id=column.column_id,
            board_id=column.board_id,
            name=column.name,
            position=column.position,
        )
