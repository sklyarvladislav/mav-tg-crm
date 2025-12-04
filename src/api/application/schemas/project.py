from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, kw_only=True)
class ProjectSchema:
    project_id: UUID | None = None
    name: str
    description: str
    status: str


@dataclass(slots=True, kw_only=True)
class ProjectUpdateSchema:
    name: str | None = None
    description: str | None = None
    status: str | None = None
