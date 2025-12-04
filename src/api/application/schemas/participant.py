from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, kw_only=True)
class ParticipantSchema:
    project_id: UUID
    user_id: int
    role: str


@dataclass(slots=True, kw_only=True)
class ParticipantUpdateSchema:
    role: str | None = None
