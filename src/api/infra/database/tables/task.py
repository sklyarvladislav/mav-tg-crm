import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column

from src.api.infra.database.tables.base import registry


@registry.mapped_as_dataclass(kw_only=True)
class Task:
    __tablename__ = "tasks"

    task_id: uuid.UUID = mapped_column(
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
    user_id: int | None = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        default=None,
    )
    project_id: uuid.UUID = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        default=None,
    )
    board_id: uuid.UUID | None = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("boards.board_id", ondelete="SET NULL"),
        default=None,
    )
    column_id: uuid.UUID | None = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("board_columns", ondelete="SET NULL"),
        default=None,
    )
    deadline: datetime | None = mapped_column(
        TIMESTAMP(timezone=True), default=None
    )
    number: int = mapped_column(Integer)
    status: str = mapped_column(String(25), default="NOT_DONE")
    priority: str = mapped_column(String(25), default="WITHOUT")
