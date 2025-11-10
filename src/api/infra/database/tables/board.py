import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column

from src.api.infra.database.tables.base import registry


@registry.mapped_as_dataclass(kw_only=True)
class Board:
    __tablename__ = "boards"

    board_id: uuid.UUID = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_id: uuid.UUID = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.project_id")
    )
    name: str = mapped_column(String(100), nullable=False)
    position: int = mapped_column(Integer, default=0)
    number_tasks: int = mapped_column(Integer, default=0)
