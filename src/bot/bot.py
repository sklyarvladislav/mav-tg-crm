import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.handlers.regist import router as regist_router
from app.handlers.start import router as start_router

from src.core.config import config

dp = Dispatcher()
bot = Bot(
    token=config.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


async def main() -> None:
    dp.include_router(start_router)
    dp.include_router(regist_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
