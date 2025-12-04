from dataclasses import asdict, dataclass
from uuid import UUID

from src.api.application.schemas.task import (
    TaskSchema,
    TaskUpdateSchema,
)
from src.api.infra.database.core.task.gates.update import UpdateTaskGate


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateTaskUsecase:
    update_task: UpdateTaskGate

    async def __call__(
        self, task_id: UUID, data: TaskUpdateSchema
    ) -> TaskSchema:
        update_data = {k: v for k, v in asdict(data).items() if v is not None}
        return await self.update_task(task_id=task_id, data=update_data)
