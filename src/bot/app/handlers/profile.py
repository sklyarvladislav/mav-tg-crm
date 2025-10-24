import app.keyboards as kb
from aiogram import F, Router
from aiogram.types import Message
from app.handlers.start import user_bd

router = Router()


@router.message(F.text == "👤 Профиль")
async def profile(message: Message) -> None:
    userid = user_bd[message.from_user.id]
    await message.answer(
        f"<b>Ваш профиль 👤</b>\n\n"
        f"Имя: {userid['name']}\n"
        f"Номер телефона: {userid['number']}\n",
        reply_markup=kb.back_from_profile,
    )


@router.message(F.text == "⬅️ Назад")
async def nazadfromprofile(message: Message) -> None:
    await message.answer("Главное меню", reply_markup=kb.main_menu)
