import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.handlers.make_project import router as make_project_router
from app.handlers.my_projects import router as my_projects_router
from app.handlers.profile import router as profile_router
from app.handlers.project_info import router as project_info_router
from app.handlers.projects import router as projects_router
from app.handlers.regist import router as regist_router
from app.handlers.settings import router as settings_router

# Импорты роутеров напрямую
from app.handlers.start import router as start_router
from app.handlers.unknownmes import router as unknownmes_router
from structlog import get_logger

from src.core.config import config

logger = get_logger()
dp = Dispatcher()
bot = Bot(
    token=config.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


async def main() -> None:
    routers = [
        start_router,
        regist_router,
        profile_router,
        settings_router,
        projects_router,
        make_project_router,
        my_projects_router,
        project_info_router,
        unknownmes_router,
    ]

    for router in routers:
        dp.include_router(router)

    logger.info("Bot start polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
