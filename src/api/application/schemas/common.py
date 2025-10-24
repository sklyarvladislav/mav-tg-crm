from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from adaptix import as_is_loader
from adaptix.conversion import ConversionRetort
from sqlalchemy.orm.attributes import Mapped

conversion_retort = ConversionRetort(
    recipe=[
        as_is_loader(Mapped),
    ]
)


@dataclass(slots=True)
class SettingsSchema:
    id: int
    settings: dict[str, Any]


@dataclass(slots=True)
class PaginationSchema:
    current: int
    page_size: int


DEFAULT_PAGINATION = PaginationSchema(current=0, page_size=10)


@dataclass(slots=True, kw_only=True)
class PagePaginatedSchema[TSchema]:
    result: list[TSchema] = field(default_factory=list)
    total: int


@dataclass(slots=True)
class OffsetIDPaginationSchema:
    offset_id: UUID | None = None


@dataclass(slots=True)
class CursorPaginationSchema:
    limit: int
    cursor: bytes | None = None


@dataclass(kw_only=True)
class CursorPaginatedSchema[TSchema]:
    result: list[TSchema]
    pagination: CursorPaginationSchema

    def __len__(self) -> int:
        return len(self.result)


@dataclass(slots=True)
class NullSchema:
    pass
