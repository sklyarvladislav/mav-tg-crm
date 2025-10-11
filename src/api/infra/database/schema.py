from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy import UnaryExpression, asc, desc
from src.application.enums.base import BaseENUM


@dataclass(slots=True)
class DatetimePaginationSchema:
    created_at: datetime


class FilterOpEnum(str, Enum):
    EQ = "eq"  # Равно
    NE = "ne"
    GT = "gt"
    LT = "lt"
    GE = "ge"
    LE = "le"
    IN = "in"
    NIN = "nin"
    LIKE = "like"
    ILIKE = "ilike"


@dataclass(slots=True)
class Filter[T]:
    op: FilterOpEnum
    value: T | None = None


class OrderEnum(BaseENUM):
    DESC = "desc"
    ASC = "asc"

    @property
    def sql(self) -> Callable[..., UnaryExpression]:
        """Метод возвращает направление сортировки для sqlalchemy.

        Returns:
            функции asc или desc
        """
        match self:
            case OrderEnum.ASC:
                return asc
            case OrderEnum.DESC:
                return desc
            case _:
                raise ValueError(f"Неизвестное значение {self}")
