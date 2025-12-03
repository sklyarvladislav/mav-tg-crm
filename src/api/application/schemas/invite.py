from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True, kw_only=True)
class InviteSchema:
    token: UUID | None = None
    project_id: UUID
    created_at: datetime | None = None
    expires_at: datetime | None = None
