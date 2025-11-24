from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select

from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import BoardColumn


@dataclass(slots=True)
class DeleteBoardColumnGate(PostgresGate):
    async def __call__(self, column_id: UUID) -> bool:
        stmt_select = select(BoardColumn).where(
            BoardColumn.column_id == column_id
        )
        column = (await self.session.execute(stmt_select)).scalar_one_or_none()

        if column is None:
            return False

        stmt_delete = delete(BoardColumn).where(
            BoardColumn.column_id == column_id
        )
        await self.session.execute(stmt_delete)
        await self.session.commit()
        return True
