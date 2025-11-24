from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from structlog import get_logger

from src.api.application.schemas.board import BoardColumnSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import BoardColumn

logger = get_logger()


@dataclass(slots=True)
class GetBoardColumnGate(PostgresGate):
    async def __call__(self, column_id: UUID) -> BoardColumnSchema:
        stmt = select(
            BoardColumn.column_id,
            BoardColumn.board_id,
            BoardColumn.name,
            BoardColumn.position,
        ).where(BoardColumn.column_id == column_id)

        return self.retort.load(
            (await self.session.execute(stmt)).mappings().fetchone(),
            BoardColumnSchema,
        )
