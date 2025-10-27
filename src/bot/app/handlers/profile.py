import app.keyboards as kb
from aiogram import F, Router
from aiogram.types import Message
from app.handlers.start import user_bd
import httpx

router = Router()


@router.message(F.text == "👤 Профиль")
async def profile(message: Message) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/auth/user/{message.from_user.id}")

    if response.status_code == 200:
        user_data = response.json()
        await message.answer(
            f"<b>Ваш профиль 👤</b>\n\n"
            f"Имя: {user_data['username']}\n"
            f"Номер телефона: {user_data['number']}\n",
            reply_markup=kb.back_from_profile,
        )
    else:
        await message.answer('Что-то пошло не так, повторите регистрацию еще раз <b>/reg</b>')


@router.message(F.text == "⬅️ Назад")
async def nazadfromprofile(message: Message) -> None:
    await message.answer("Главное меню", reply_markup=kb.main_menu)
