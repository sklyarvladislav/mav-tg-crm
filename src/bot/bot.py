import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from src.core.config import config
from structlog import get_logger

logger = get_logger()


async def main():
    bot = Bot(token=config.bot.token)
    dp = Dispatcher()

    @dp.message(Command(commands=["start"]))
    async def start_handler(message: types.Message):
        await message.reply("Привет! Я эхо-бот.")

    @dp.message()
    async def echo_handler(message: types.Message):
        await message.answer(message.text)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("bot started")
    asyncio.run(main())
