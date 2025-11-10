from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, kw_only=True)
class BoardSchema:
    board_id: UUID | None = None
    project_id: UUID
    name: str
    position: int = 0
    number_tasks: int = 0


@dataclass(slots=True, kw_only=True)
class BoardUpdateSchema:
    name: str | None = None
    position: int | None = None
    number_tasks: int | None = None
