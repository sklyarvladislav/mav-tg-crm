from dataclasses import dataclass
from uuid import UUID

from src.api.application.schemas.task import TaskSchema
from src.api.infra.database.core.task.gates.get import GetTaskGate


@dataclass(slots=True, frozen=True, kw_only=True)
class GetTaskUsecase:
    get_task: GetTaskGate

    async def __call__(self, task_id: UUID) -> TaskSchema:
        task: TaskSchema = await self.get_task(task_id=task_id)

        return TaskSchema(
            task_id=task.task_id,
            name=task.name,
            text=task.text,
            document_id=task.document_id,
            user_id=task.user_id,
            project_id=task.project_id,
            board_id=task.board_id,
            column_id=task.column_id,
            deadline=task.deadline,
            status=task.status,
            priority=task.priority,
        )
