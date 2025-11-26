import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from app.handlers.board.create import router as board_router
from app.handlers.document.create import router as document_router
from app.handlers.document.delete import (
    router as delete_document_router,
)
from app.handlers.document.get import router as get_document_router
from app.handlers.project.back_to_project import (
    router as back_to_project_router,
)
from app.handlers.project.create import router as make_project_router
from app.handlers.project.my_projects import router as my_projects_router
from app.handlers.project.project_info import router as project_info_router
from app.handlers.project.project_settings import (
    router as project_settings_router,
)
from app.handlers.project.projects import router as projects_router
from app.handlers.start import router as start_router
from app.handlers.user.profile import router as profile_router
from app.handlers.user.regist import router as regist_router
from app.handlers.user.settings import router as settings_router
from app.handlers.user.unknownmes import router as unknownmes_router
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
        projects_router,
        document_router,
        delete_document_router,
        make_project_router,
        my_projects_router,
        project_settings_router,
        project_info_router,
        back_to_project_router,
        unknownmes_router,
        board_router,
        get_document_router,
    ]

    for router in routers:
        dp.include_router(router)

    await dp.start_polling(bot)
    logger.info("Bot start polling")


if __name__ == "__main__":
    asyncio.run(main())
