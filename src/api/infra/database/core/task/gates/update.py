from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from sqlalchemy import update
from structlog import get_logger

from src.api.application.schemas.task import TaskSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Task

logger = get_logger()


@dataclass(slots=True)
class UpdateTaskGate(PostgresGate):
    async def __call__(self, task_id: UUID, data: dict) -> TaskSchema:
        for k, v in data.items():
            if isinstance(v, Enum):
                data[k] = v.value

        stmt = (
            update(Task)
            .where(Task.task_id == task_id)
            .values(**data)
            .returning(
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
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        row = result.mappings().fetchone()
        if row is not None:
            row = dict(row)
            for k, v in row.items():
                if isinstance(v, Enum):
                    row[k] = v.value

        return self.retort.load(
            row,
            TaskSchema,
        )
