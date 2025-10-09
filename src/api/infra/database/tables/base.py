from typing import Any

from sqlalchemy import Column, MetaData, Table
from sqlalchemy.orm import registry
from sqlalchemy.sql.expression import text

SCHEMA = "mav_schema"

enabled_pg_schemas: list = [
    "__alembic_schema",
    SCHEMA,
]

metadata = MetaData(schema=SCHEMA)
registry = registry(metadata=metadata)


@registry.as_declarative_base()
class BaseDB:
    __tablename__: str


def group_by_fields(
    table: Table | BaseDB, exclude: list[str] | None = None
) -> list:
    """Берем имена всех колонок для группировки.

    Returns:
        list[колонка]
    """

    payload = []
    if not exclude:
        exclude = []

    for column in table.columns:
        if column.key in exclude:
            continue

        payload.append(column)

    return payload


def jsonb_build_object(
    table: Table,
) -> list[Any]:
    """Build jsonb object для модели.

    Returns:
        list[ключ колонки, колонка]
    """

    payload = []
    column: Column
    for column in table.columns:
        payload.append(text(f"'{column.key}'::TEXT"))
        payload.append(column)

    return payload
