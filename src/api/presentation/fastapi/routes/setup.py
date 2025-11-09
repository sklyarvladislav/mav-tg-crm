from fastapi import FastAPI
from structlog import get_logger

from src.api.presentation.fastapi.routes.auth import (
    router as auth_router,
)
from src.api.presentation.fastapi.routes.document import (
    router as document_router,
)
from src.api.presentation.fastapi.routes.healthcheck import (
    router as healthcheck_router,
)
from src.api.presentation.fastapi.routes.project import (
    router as project_router,
)
from src.api.presentation.fastapi.routes.user import router as user_router

logger = get_logger()


def setup_routes(app: FastAPI) -> None:
    app.include_router(healthcheck_router)
    app.include_router(auth_router, prefix="/auth")
    app.include_router(user_router, prefix="/user", tags=["User"])
    app.include_router(project_router, prefix="/project", tags=["Project"])
    app.include_router(document_router, prefix="/document", tags=["Document"])
    logger.info("routes set up")
