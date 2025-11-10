from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from structlog import get_logger

from src.api.application.schemas.board import BoardSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Board

logger = get_logger()


@dataclass(slots=True)
class GetBoardGate(PostgresGate):
    async def __call__(self, board_id: UUID) -> BoardSchema:
        stmt = select(
            Board.board_id,
            Board.project_id,
            Board.name,
            Board.position,
            Board.number_tasks,
        ).where(Board.board_id == board_id)

        return self.retort.load(
            (await self.session.execute(stmt)).mappings().fetchone(),
            BoardSchema,
        )
