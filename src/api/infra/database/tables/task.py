import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column

from src.api.infra.database.tables.base import registry


@registry.mapped_as_dataclass(kw_only=True)
class Task:
    __tablename__ = "tasks"

    tasks_id: uuid.UUID = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: str = mapped_column(String(100), nullable=False)
    text: str | None = mapped_column(Text, default=None)
    document_id: uuid.UUID | None = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.document_id", ondelete="SET NULL"),
        default=None,
    )
    responsible_id: int = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    project_id: uuid.UUID = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        nullable=False,
    )
    board_id: uuid.UUID | None = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("boards.board_id", ondelete="SET NULL"),
        default=None,
    )
    deadline: datetime | None = mapped_column(
        TIMESTAMP(timezone=True), default=None
    )
    status: str | None = mapped_column(String(50), default=None)
    priority: str | None = mapped_column(String(25), default=None)
