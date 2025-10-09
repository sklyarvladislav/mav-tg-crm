from fastapi import FastAPI
from structlog import get_logger
from structlog.typing import FilteringBoundLogger

from src.api.presentation.fastapi.routes.setup import setup_routes
from src.core.config import Config

logger = get_logger()


def setup_fastapi(_config: Config, logger: FilteringBoundLogger) -> FastAPI:
    app = FastAPI(docs_url="/api", logger=logger)
    setup_routes(app)

    return app
