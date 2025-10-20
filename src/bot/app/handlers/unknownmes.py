from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message()
async def handle_unknown(message: Message) -> None:
    await message.answer("Напишите /start для вызова меню.")