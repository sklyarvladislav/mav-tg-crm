from collections.abc import AsyncIterable

import structlog
from dishka import Provider, Scope, provide, provide_all
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from src.api.infra.database.services.pagination.cursor import (
    CursorPaginationService,
)
from src.api.infra.database.services.pagination.offset import (
    OffsetPaginationService,
)

from src.api.infra.database.admin.settings.gates import (
    GetSettingsGate,
    UpdateSettingsGate,
)
from src.api.infra.database.common import (
    CreateGate,
    DeleteGate,
    GetOneGate,
    GetPaginatedGate,
    UpdateGate,
)
from src.api.infra.database.core.version.gates import GetVersionsGate
from src.core.config import Config

logger = structlog.get_logger()


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    async def _get_engine(self, config: Config) -> AsyncIterable[AsyncEngine]:
        engine: AsyncEngine | None = None
        try:
            if engine is None:
                engine = create_async_engine(config.database.dsn)

            yield engine
        except ConnectionRefusedError as e:
            logger.error("Error connecting to database", error=e)
        finally:
            if engine is not None:
                await engine.dispose()

    @provide(scope=Scope.REQUEST)
    async def _get_session(
        self, engine: AsyncEngine
    ) -> AsyncIterable[AsyncSession]:
        async with async_sessionmaker(
            engine, expire_on_commit=False
        )() as session:
            yield session

    _get_services = provide_all(
        OffsetPaginationService,
        CursorPaginationService,
        scope=Scope.APP,
    )

    _get_base_gates = provide_all(
        GetPaginatedGate,
        GetOneGate,
        CreateGate,
        UpdateGate,
        DeleteGate,
        scope=Scope.REQUEST,
    )

    _get_gateways = provide_all(
        GetSettingsGate,
        GetVersionsGate,
        UpdateSettingsGate,
        scope=Scope.REQUEST,
    )
