import app.keyboards as kb
from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
import httpx

user_bd = {
    123456: {"name": "Alex", "number": "+71231231212"},
    62342462: {"name": "Makar", "number": "+79119119191"},
}

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/auth/user/{message.from_user.id}")

    if response.status_code == 200:
        user_data = response.json()
        await message.answer(
            f"С возвращением, <b>{user_data['username']}</b>!",
            reply_markup=kb.main_menu,
        )
    else:
        await message.answer(
            "Добро пожаловать!\nДля дальнейшей работы бота <b>нужно пройти регистрацию</b>, для этого пропишите <b>/reg</b> 🎯",
            reply_markup=types.ReplyKeyboardRemove(),
        )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.reply("Для перезапуска бота напишите <b>/start</b>")
