import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import mapped_column

from src.api.infra.database.tables.base import registry


@registry.mapped_as_dataclass(kw_only=True)
class Document:
    __tablename__ = "documents"

    document_id: uuid.UUID = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    project_id: uuid.UUID | None = mapped_column(
        ForeignKey("projects.project_id")
    )
    name: str = mapped_column(String(100), nullable=False)
    link: str = mapped_column(String(100), nullable=False)
