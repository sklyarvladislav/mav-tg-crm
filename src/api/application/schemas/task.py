from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.api.application.enums.task import PriorityTask, StatusTask


@dataclass(slots=True, kw_only=True)
class TaskSchema:
    task_id: UUID
    name: str
    text: str
    document_id: UUID | None
    user_id: int | None
    project_id: UUID
    board_id: UUID | None
    deadline: datetime
    status: StatusTask
    priority: PriorityTask


@dataclass(slots=True, kw_only=True)
class TaskUpdateSchema:
    name: str | None = None
    text: str | None = None
    document_id: UUID | None = None
    responsible_id: int | None = None
    project_id: UUID | None = None
    board_id: UUID | None = None
    deadline: datetime | None = None
    status: StatusTask | None = None
    priority: PriorityTask | None = None
