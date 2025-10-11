from dataclasses import dataclass

from sqlalchemy import func, select
from src.api.application.schemas.version import FullVersionSchema

from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Version


@dataclass(slots=True)
class GetVersionsGate(PostgresGate):
    async def __call__(
        self, offset_id: int | None, limit: int
    ) -> list[FullVersionSchema]:
        stmt = (
            select(
                Version.id,
                func.concat(
                    Version.major,
                    ".",
                    Version.minor,
                    ".",
                    Version.patch,
                ).label("version"),
                Version.description,
            )
            .limit(limit)
            .order_by(Version.id.desc())
        )
        if offset_id is not None:
            stmt = stmt.where(Version.id < offset_id)

        result = (await self.session.execute(stmt)).mappings().fetchall()
        return self.retort.load(result, list[FullVersionSchema])
