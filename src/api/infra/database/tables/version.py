from sqlalchemy import Integer, Text, UniqueConstraint
from sqlalchemy.orm import mapped_column

from src.api.infra.database.tables.base import registry


@registry.mapped_as_dataclass(kw_only=True)
class Version:
    __tablename__ = "versions"

    id: int = mapped_column(Integer, primary_key=True)
    major: int = mapped_column(Integer, nullable=False)
    minor: int = mapped_column(Integer, nullable=False)
    patch: str = mapped_column(Text, nullable=False)
    description: str = mapped_column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("major", "minor", "patch"),)
