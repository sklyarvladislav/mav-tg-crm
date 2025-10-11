from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column

from src.api.infra.database.tables.base import registry


@registry.mapped_as_dataclass(kw_only=True)
class Users:
    __tablename__ = "users"

    user_id: int = mapped_column(primary_key=True, default=1)
    username: str = mapped_column(String(50), nullable=False)
    number: int = mapped_column(Integer, nullable=False)
