from collections.abc import AsyncIterable

import structlog
from dishka import Provider, Scope, provide, provide_all
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.api.infra.database.admin.settings.gates import (
    GetSettingsGate,
    UpdateSettingsGate,
)
from src.api.infra.database.common import (
    CreateGate,
    DeleteGate,
    GetOneGate,
    UpdateGate,
)
from src.api.infra.database.core.board.gates.delete import DeleteBoardGate
from src.api.infra.database.core.board.gates.get import GetBoardGate
from src.api.infra.database.core.board.gates.update import UpdateBoardGate
from src.api.infra.database.core.column.gates.delete import (
    DeleteBoardColumnGate,
)
from src.api.infra.database.core.column.gates.get import GetBoardColumnGate
from src.api.infra.database.core.column.gates.update import (
    UpdateBoardColumnGate,
)
from src.api.infra.database.core.document.gates.delete import (
    DeleteDocumentGate,
)
from src.api.infra.database.core.document.gates.get import GetDocumentGate
from src.api.infra.database.core.document.gates.update import (
    UpdateDocumentGate,
)
from src.api.infra.database.core.project.gates.delete import DeleteProjectGate
from src.api.infra.database.core.project.gates.get import GetProjectGate
from src.api.infra.database.core.project.gates.update import UpdateProjectGate
from src.api.infra.database.core.task.gates.delete import DeleteTaskGate
from src.api.infra.database.core.task.gates.get import GetTaskGate
from src.api.infra.database.core.task.gates.update import UpdateTaskGate
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
        scope=Scope.APP,
    )

    _get_base_gates = provide_all(
        GetOneGate,
        CreateGate,
        UpdateGate,
        DeleteGate,
        GetProjectGate,
        UpdateProjectGate,
        DeleteProjectGate,
        GetDocumentGate,
        DeleteDocumentGate,
        UpdateDocumentGate,
        GetBoardGate,
        DeleteBoardGate,
        UpdateBoardGate,
        GetBoardColumnGate,
        DeleteBoardColumnGate,
        UpdateBoardColumnGate,
        GetTaskGate,
        DeleteTaskGate,
        UpdateTaskGate,
        scope=Scope.REQUEST,
    )

    _get_gateways = provide_all(
        GetSettingsGate,
        GetVersionsGate,
        UpdateSettingsGate,
        scope=Scope.REQUEST,
    )
