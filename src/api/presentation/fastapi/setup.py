from fastapi import FastAPI
from structlog import get_logger

from src.config import Config
from src.presentation.fastapi.routes.setup import setup_routes

logger = get_logger()


def setup_fastapi(config: Config, logger) -> FastAPI:
    app = FastAPI(docs_url="/api", logger=logger)
    setup_routes(app)

    return app
