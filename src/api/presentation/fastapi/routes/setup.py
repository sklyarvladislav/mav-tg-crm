from fastapi import FastAPI
from structlog import get_logger

from src.api.presentation.fastapi.routes.healthcheck import (
    router as healthcheck_router,
)

logger = get_logger()


def setup_routes(app: FastAPI) -> None:
    app.include_router(healthcheck_router)
    logger.info("routes set up")
