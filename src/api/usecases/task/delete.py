from dataclasses import dataclass
from uuid import UUID

from src.api.infra.database.core.task.gates.delete import DeleteTaskGate


@dataclass(slots=True, frozen=True, kw_only=True)
class DeleteTaskUsecase:
    delete_task: DeleteTaskGate

    async def __call__(self, task_id: UUID) -> bool:
        return await self.delete_task(task_id=task_id)
