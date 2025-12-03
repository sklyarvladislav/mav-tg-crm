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
from src.api.infra.database.core.board.gates import (
    DeleteBoardGate,
    GetBoardGate,
    UpdateBoardGate,
)
from src.api.infra.database.core.column.gates import (
    DeleteBoardColumnGate,
    GetBoardColumnGate,
    UpdateBoardColumnGate,
)
from src.api.infra.database.core.document.gates import (
    DeleteDocumentGate,
    GetDocumentGate,
    UpdateDocumentGate,
)
from src.api.infra.database.core.participant.gates import (
    DeleteParticipantGate,
    GetParticipantGate,
    UpdateParticipantGate,
)
from src.api.infra.database.core.project.gates import (
    DeleteProjectGate,
    GetProjectGate,
    UpdateProjectGate,
)
from src.api.infra.database.core.task.gates import (
    DeleteTaskGate,
    GetTaskGate,
    UpdateTaskGate,
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
        scope=Scope.APP,
    )

    _get_base_gates = provide_all(
        # Gates
        GetOneGate,
        CreateGate,
        UpdateGate,
        DeleteGate,
        # Project
        GetProjectGate,
        UpdateProjectGate,
        DeleteProjectGate,
        # Participant
        DeleteParticipantGate,
        GetParticipantGate,
        UpdateParticipantGate,
        # Document
        GetDocumentGate,
        DeleteDocumentGate,
        UpdateDocumentGate,
        # Board
        GetBoardGate,
        DeleteBoardGate,
        UpdateBoardGate,
        # Board Column
        GetBoardColumnGate,
        DeleteBoardColumnGate,
        UpdateBoardColumnGate,
        # Task
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
