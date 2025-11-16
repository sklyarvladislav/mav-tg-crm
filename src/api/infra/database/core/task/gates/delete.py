from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select

from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Task


@dataclass(slots=True)
class DeleteTaskGate(PostgresGate):
    async def __call__(self, task_id: UUID) -> bool:
        stmt_select = select(Task).where(Task.task_id == task_id)
        task = (await self.session.execute(stmt_select)).scalar_one_or_none()

        if task is None:
            return False

        stmt_delete = delete(Task).where(Task.task_id == task_id)
        await self.session.execute(stmt_delete)
        await self.session.commit()
        return True
