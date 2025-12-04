from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True, kw_only=True)
class TaskSchema:
    task_id: UUID
    name: str
    text: str
    document_id: UUID | None = None
    user_id: int | None = None
    project_id: UUID
    board_id: UUID | None = None
    column_id: UUID | None = None
    deadline: datetime | None = None
    number: int = 0
    status: str = "NOT_DONE"
    priority: str = "WITHOUT"


@dataclass(slots=True, kw_only=True)
class TaskUpdateSchema:
    name: str | None = None
    text: str | None = None
    document_id: UUID | None = None
    responsible_id: int | None = None
    project_id: UUID | None = None
    board_id: UUID | None = None
    column_id: UUID | None = None
    deadline: datetime | None = None
    number: int | None = None
    status: str | None = None
    priority: str | None = None
