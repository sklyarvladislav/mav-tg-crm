from typing import Any

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column

from src.api.infra.database.tables.base import registry


@registry.mapped_as_dataclass(kw_only=True)
class Settings:
    __tablename__ = "settings"

    id: int = mapped_column(primary_key=True, default=1)
    settings: dict[str, Any] = mapped_column(JSONB, nullable=False)
