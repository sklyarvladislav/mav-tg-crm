from dataclasses import asdict, dataclass
from uuid import UUID

from src.api.application.schemas.board import (
    BoardColumnSchema,
    BoardColumnUpdateSchema,
)
from src.api.infra.database.core.column.gates import (
    UpdateBoardColumnGate,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateBoardColumnUsecase:
    update_column: UpdateBoardColumnGate

    async def __call__(
        self, column_id: UUID, data: BoardColumnUpdateSchema
    ) -> BoardColumnSchema:
        update_data = {k: v for k, v in asdict(data).items() if v is not None}
        return await self.update_column(column_id=column_id, data=update_data)
