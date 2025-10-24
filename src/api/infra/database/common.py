from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

import structlog
from adaptix import Retort, as_is_loader, name_mapping
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import Mapped
from sqlalchemy.sql import Delete, Insert, Select
from sqlalchemy.sql.dml import Update
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.schema import Column
from typing_extensions import Self

from src.api.infra.database.errors import (
    CreateError,
    DatabaseError,
    NotFoundError,
    UpdateError,
)

logger = structlog.get_logger()

retort = Retort(
    recipe=[
        name_mapping(omit_default=True),
        as_is_loader(UUID),
        as_is_loader(datetime),
        as_is_loader(Mapped),
    ]
)

WhereClause = ColumnElement[bool]


@dataclass(kw_only=True)
class WhereClauseMixin:
    _query: Select | Insert | Update | Delete | None = field(
        default=None, init=False
    )

    def with_condition(self, *conditions: WhereClause) -> Self:
        self._query = self._query.where(*conditions)
        return self

    def with_id(self, ids: list[Any], field: str = "id") -> Self:
        self._query = self._query.where(Column(field) == ids)
        return self

    def with_ids(self, ids: list[Any], field: str = "id") -> Self:
        self._query = self._query.where(Column(field).in_(ids))
        return self

    def with_bulk_id(self, ids: list[Any], field: str = "id") -> Self:
        self._query = self._query.where(Column(field).in_(ids))
        return self

    def with_user(self, user_id: UUID, field: str = "created_by") -> Self:
        self._query = self._query.where(Column(field) == user_id)
        return self


@dataclass(kw_only=True)
class ReturningMixin[TTable]:
    table: type[TTable]
    _query: Insert | Update = field(init=False)
    _returning: bool = field(default=False, init=False)

    def returning(self) -> "ReturningMixin[TTable]":
        self._returning = True
        self._query = self._query.returning(self.table)
        return self

    async def __call__(self, *args: object, **kwds: object) -> TTable: ...


@dataclass(kw_only=True)
class PostgresGate:
    session: AsyncSession
    retort = retort


@dataclass(kw_only=True)
class CreateGate[TTable, TCreate](PostgresGate, ReturningMixin[TTable]):
    table: type[TTable]
    create_schema_type: type[TCreate]

    _query: Insert = field(init=False)
    _extra_insert: dict[str, Any] = field(default_factory=dict, init=False)
    _omit: set[str] = field(default_factory=set, init=False)

    def __post_init__(self) -> None:
        self._query = insert(self.table)

    def with_omit(self, *fields: str) -> "CreateGate[TTable, TCreate]":
        self._omit.update(*fields)
        return self

    def with_field(
        self, field: str, value: object
    ) -> "CreateGate[TTable, TCreate]":
        self._extra_insert[field] = value
        return self

    def with_user(
        self, user_id: UUID, field: str = "created_by"
    ) -> "CreateGate[TTable, TCreate]":
        self._extra_insert[field] = user_id
        return self

    async def __call__(self, entity: TCreate) -> TTable | None:
        stmt = self._query.values(
            **{
                f: v
                for f, v in retort.dump(entity).items()
                if f not in self._omit
            },
            **self._extra_insert,
        )
        try:
            result = await self.session.execute(stmt)
            if result is None:
                raise CreateError(
                    model_name=str(self.table), error="no result"
                )
            if not self._returning:
                return None
            result = result.scalar_one_or_none()
            if result is None:
                raise CreateError(
                    model_name=str(self.table), error="no result"
                )
            return result
        except IntegrityError as e:
            raise CreateError(model_name=str(self.table), error=str(e)) from e


@dataclass(kw_only=True)
class GetOneGate[TTable](PostgresGate, WhereClauseMixin):
    table: type[TTable]

    _query: Select = field(init=False)
    _omit: set[str] = field(default_factory=set, init=False)

    def __post_init__(self) -> None:
        self._query = select(self.table)

    async def __call__(self) -> TTable:
        result = (await self.session.execute(self._query)).scalar_one_or_none()
        if result is None:
            raise NotFoundError(str(self.table))

        return result


@dataclass(kw_only=True)
class DeleteGate[TTable](PostgresGate, WhereClauseMixin):
    table: type[TTable]

    _query: Delete = field(init=False)
    _truncate: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        self._query = delete(self.table)

    def truncate(self) -> "DeleteGate[TTable]":
        self._truncate = True
        return self

    async def __call__(
        self,
    ) -> None:
        stmt = self._query if not self._truncate else delete(self.table)
        try:
            result = await self.session.execute(stmt)
            if result.rowcount != 1:
                raise NotFoundError(model_name=str(self.table))

        except IntegrityError as e:
            raise DatabaseError(message=str(e)) from e


@dataclass(kw_only=True)
class UpdateGate[TTable, TUpdate](
    PostgresGate, ReturningMixin[TTable], WhereClauseMixin
):
    table: type[TTable]
    update_schema_type: type[TUpdate]

    _query: Update = field(init=False)
    _extra_insert: dict[str, Any] = field(default_factory=dict, init=False)
    _omit: set[str] = field(default_factory=set, init=False)

    def __post_init__(self) -> None:
        self._query = update(self.table)

    def with_omit(self, *fields: str) -> "UpdateGate[TTable, TUpdate]":
        self._omit.update(*fields)
        return self

    def with_field(
        self, field: str, value: object
    ) -> "UpdateGate[TTable, TUpdate]":
        self._extra_insert[field] = value
        return self

    async def __call__(self, entity: TUpdate) -> TTable | None:
        stmt = self._query.values(**retort.dump(entity))
        try:
            result = await self.session.execute(stmt)
            if not self._returning:
                if result.rowcount == 0:
                    raise UpdateError(
                        model_name=str(self.table), error="no result"
                    )
                return None
            result = result.scalar_one_or_none()
            if result is None:
                raise UpdateError(
                    model_name=str(self.table), error="no result"
                )

            return result
        except IntegrityError as e:
            raise UpdateError(model_name=str(self.table), error=str(e)) from e
