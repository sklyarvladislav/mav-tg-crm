from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import update
from structlog import get_logger

from src.api.application.schemas.board import BoardColumnSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import BoardColumn

logger = get_logger()


@dataclass(slots=True)
class UpdateBoardColumnGate(PostgresGate):
    async def __call__(self, column_id: UUID, data: dict) -> BoardColumnSchema:
        stmt = (
            update(BoardColumn)
            .where(BoardColumn.column_id == column_id)
            .values(**data)
            .returning(
                BoardColumn.column_id,
                BoardColumn.board_id,
                BoardColumn.name,
                BoardColumn.position,
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return self.retort.load(
            (result.mappings().fetchone()),
            BoardColumnSchema,
        )
