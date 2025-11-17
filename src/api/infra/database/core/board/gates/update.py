from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import update
from structlog import get_logger

from src.api.application.schemas.board import BoardSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Board

logger = get_logger()


@dataclass(slots=True)
class UpdateBoardGate(PostgresGate):
    async def __call__(self, board_id: UUID, data: dict) -> BoardSchema:
        stmt = (
            update(Board)
            .where(Board.board_id == board_id)
            .values(**data)
            .returning(
                Board.board_id,
                Board.project_id,
                Board.name,
                Board.position,
                Board.number_tasks,
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return self.retort.load(
            (result.mappings().fetchone()),
            BoardSchema,
        )
