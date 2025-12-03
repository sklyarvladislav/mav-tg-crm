from fastapi import FastAPI
from structlog import get_logger

from src.api.presentation.fastapi.routes.auth import (
    router as auth_router,
)
from src.api.presentation.fastapi.routes.board import (
    router as board_router,
)
from src.api.presentation.fastapi.routes.column import (
    router as column_router,
)
from src.api.presentation.fastapi.routes.document import (
    router as document_router,
)
from src.api.presentation.fastapi.routes.healthcheck import (
    router as healthcheck_router,
)
from src.api.presentation.fastapi.routes.participant import (
    router as participant_router,
)
from src.api.presentation.fastapi.routes.project import (
    router as project_router,
)
from src.api.presentation.fastapi.routes.task import router as task_router
from src.api.presentation.fastapi.routes.user import router as user_router

logger = get_logger()


def setup_routes(app: FastAPI) -> None:
    app.include_router(healthcheck_router)
    app.include_router(auth_router, prefix="/auth")
    app.include_router(user_router, prefix="/user", tags=["User"])
    app.include_router(project_router, prefix="/project", tags=["Project"])
    app.include_router(document_router, prefix="/document", tags=["Document"])
    app.include_router(board_router, prefix="/board", tags=["Board"])
    app.include_router(
        column_router, prefix="/column", tags=["Columns of board"]
    )
    app.include_router(task_router, prefix="/task", tags=["Task"])
    app.include_router(
        participant_router, prefix="/participant", tags=["Participant"]
    )
    logger.info("Routes set up")
