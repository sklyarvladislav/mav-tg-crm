from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, kw_only=True)
class DocumentSchema:
    document_id: UUID | None = None
    project_id: UUID
    name: str
    link: str


@dataclass(slots=True, kw_only=True)
class DocumentUpdateSchema:
    name: str | None = None
    link: str | None = None
