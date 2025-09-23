from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from structlog import get_logger
from src.config import Config, config
from src.main.di import DishkaProvider
from src.presentation.fastapi.setup import setup_fastapi
from src.usecases.provider import UsecaseProvider

logger = get_logger()

app = setup_fastapi(config, logger)

container = make_async_container(
    DishkaProvider(), UsecaseProvider(), context={Config: config}
)

setup_dishka(container, app)
