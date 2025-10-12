from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

user_bd = {
    123456: {"name": "Alex", "number": "+71231231212"},
    62342462: {"name": "Makar", "number": "+79119119191"},
}

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    if message.from_user.id in user_bd:
        await message.answer(
            f"С возвращением, <b>{user_bd[message.from_user.id]['name']}</b>! Ты уже зарегистрирован"
        )
    else:
        await message.answer(
            "Добро пожаловать!\nДля дальнейшей работы бота <b>нужно пройти регистрацию</b>, для этого пропишите <b>/reg</b>"
        )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.reply("Для перезапуска бота напишите <b>/start</b>")
