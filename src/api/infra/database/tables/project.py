import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column

from src.api.infra.database.tables.base import registry


@registry.mapped_as_dataclass(kw_only=True)
class Project:
    __tablename__ = "projects"

    project_id: uuid.UUID = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: str = mapped_column(String(100), nullable=False)
    description: str | None = mapped_column(Text)
    status: str | None = mapped_column(String(25), default=None)
    owner: int | None = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE")
    )
    created_at: datetime = mapped_column(
        TIMESTAMP, default=datetime.utcnow, nullable=False
    )


@registry.mapped_as_dataclass(kw_only=True)
class ProjectParticipant:
    __tablename__ = "project_participants"

    project_id: uuid.UUID = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: int = mapped_column(
        Integer,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: str | None = mapped_column(String(50))
    added_at: datetime = mapped_column(
        TIMESTAMP, default=datetime.utcnow, nullable=False
    )
