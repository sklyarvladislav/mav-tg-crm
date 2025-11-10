from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select

from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Board


@dataclass(slots=True)
class DeleteBoardGate(PostgresGate):
    async def __call__(self, board_id: UUID) -> bool:
        stmt_select = select(Board).where(Board.board_id == board_id)
        board = (await self.session.execute(stmt_select)).scalar_one_or_none()

        if board is None:
            return False

        stmt_delete = delete(Board).where(Board.board_id == board_id)
        await self.session.execute(stmt_delete)
        await self.session.commit()
        return True
