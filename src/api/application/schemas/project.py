from dataclasses import dataclass
from uuid import UUID

from src.api.application.enums.project import StatusProject


@dataclass(slots=True, kw_only=True)
class ProjectSchema:
    project_id: UUID | None = None
    name: str
    description: str
    status: StatusProject
    owner: int


@dataclass(slots=True, kw_only=True)
class ProjectUpdateSchema:
    name: str | None = None
    description: str | None = None
    status: StatusProject | None = None
    owner: int | None = None
