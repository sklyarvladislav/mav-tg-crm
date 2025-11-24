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


@dataclass(slots=True, kw_only=True)
class BoardColumnSchema:
    column_id: UUID | None = None
    board_id: UUID
    name: str
    position: int


@dataclass(slots=True, kw_only=True)
class BoardColumnUpdateSchema:
    column_id: UUID | None = None
    board_id: UUID | None = None
    name: str | None = None
    position: int | None = None
