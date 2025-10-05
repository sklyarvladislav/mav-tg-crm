from dataclasses import dataclass, field

from src.api.infra.database.services.filtering.schema import Filter
from src.api.infra.database.services.ordering.schema import OrderEnum

from src.api.infra.database.admin.schema import update_schema


@dataclass(slots=True)
class FilterVersionSchema:
    major: Filter[int] | None = field(default=None)
    minor: Filter[int] | None = field(default=None)
    patch: Filter[str] | None = field(default=None)


@dataclass(slots=True)
class OrderVersionSchema:
    major: OrderEnum | None = None
    minor: OrderEnum | None = None
    patch: OrderEnum | None = None


@dataclass(slots=True)
class CreateVersionSchema:
    major: int
    minor: int
    patch: str
    description: str


@update_schema
@dataclass(slots=True)
class UpdateVersionSchema:
    major: int | None = None
    minor: int | None = None
    patch: str | None = None
    description: str | None = None
