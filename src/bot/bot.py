import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from app.handlers.board import make_board_router
from app.handlers.document import (
    delete_document_router,
    get_document_router,
    make_document_router,
)
from app.handlers.project import (
    make_project_router,
    my_projects_router,
    project_info_router,
    project_settings_router,
    projects_router,
)
from app.handlers.start import router as start_router
from app.handlers.user import (
    profile_router,
    regist_router,
    settings_router,
    unknownmes_router,
)
from structlog import get_logger

from src.core.config import config

logger = get_logger()
dp = Dispatcher()
bot = Bot(
    token=config.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="/start", description="Старт"),
        BotCommand(command="/menu", description="Главное меню"),
        BotCommand(command="/about", description="О сервисе"),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    await set_commands(bot)

    routers = [
        start_router,
        regist_router,
        profile_router,
        settings_router,
        # project
        projects_router,
        make_project_router,
        my_projects_router,
        project_settings_router,
        project_info_router,
        # document
        make_document_router,
        get_document_router,
        delete_document_router,
        # board
        make_board_router,
        # unknownmes
        unknownmes_router,
    ]
    for r in routers:
        dp.include_router(r)
        for name, value in globals().items():
            if value == r:
                logger.info(f"Route: {name} - set up")

    await dp.start_polling(bot)
    logger.info("Bot start polling")


if __name__ == "__main__":
    asyncio.run(main())
