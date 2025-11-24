from dataclasses import dataclass
from uuid import UUID

from src.api.infra.database.core.column.gates.delete import (
    DeleteBoardColumnGate,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class DeleteBoardColumnUsecase:
    delete_column: DeleteBoardColumnGate

    async def __call__(self, column_id: UUID) -> bool:
        return await self.delete_column(column_id=column_id)
