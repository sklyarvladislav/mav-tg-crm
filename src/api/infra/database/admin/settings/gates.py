from dataclasses import dataclass
from typing import Any

from sqlalchemy import insert, select, text, update

from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Settings


@dataclass(slots=True, kw_only=True)
class GetSettingsGate(PostgresGate):
    async def __call__(self) -> Settings:
        """Получает объект настроек или создаёт пустой, если не существует."""
        result = (
            await self.session.execute(
                select(Settings).where(Settings.id == 1)
            )
        ).scalar_one_or_none()
        if not result:
            result = (
                await self.session.execute(
                    insert(Settings)
                    .values(id=1, settings=text("'{}'::jsonb"))
                    .returning(Settings)
                )
            ).scalar_one_or_none()
        return result


@dataclass(slots=True, kw_only=True)
class UpdateSettingsGate(PostgresGate):
    async def __call__(self, settings: dict[str, Any]) -> Settings:
        """Update the base prompt."""
        result = (
            await self.session.execute(
                update(Settings)
                .where(Settings.id == 1)
                .values(settings=settings)
                .returning(Settings)
            )
        ).scalar_one_or_none()
        if not result:
            result = (
                await self.session.execute(
                    insert(Settings)
                    .values(id=1, settings=settings)
                    .returning(Settings)
                )
            ).scalar_one_or_none()
        return result
