from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from structlog import get_logger

from src.api.application.schemas.task import TaskSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Task

logger = get_logger()


@dataclass(slots=True)
class GetTaskGate(PostgresGate):
    async def __call__(self, task_id: UUID) -> TaskSchema:
        stmt = select(
            Task.task_id,
            Task.name,
            Task.text,
            Task.document_id,
            Task.user_id,
            Task.project_id,
            Task.board_id,
            Task.column_id,
            Task.deadline,
            Task.status,
            Task.priority,
        ).where(Task.task_id == task_id)

        return self.retort.load(
            (await self.session.execute(stmt)).mappings().fetchone(),
            TaskSchema,
        )
