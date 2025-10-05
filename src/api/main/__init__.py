from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from structlog import get_logger

from src.api.main.di import DishkaProvider
from src.api.presentation.fastapi.setup import setup_fastapi
from src.api.usecases.provider import UsecaseProvider
from src.core.config import Config, config

logger = get_logger()

app = setup_fastapi(config, logger)

container = make_async_container(
    DishkaProvider(), UsecaseProvider(), context={Config: config}
)

setup_dishka(container, app)
