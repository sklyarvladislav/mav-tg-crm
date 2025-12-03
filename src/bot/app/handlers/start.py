import app.keyboards as kb
import httpx
from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from fastapi import status

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    text = message.text or ""
    user_id = message.from_user.id

    async with httpx.AsyncClient() as client:
        # Проверяем, есть ли пользователь в базе
        response = await client.get(f"http://web:80/user/{user_id}")

    if response.status_code == status.HTTP_200_OK:
        user_data = response.json()

        # Проверяем, пришёл ли токен приглашения
        if text.startswith("/start join_"):
            token = text.split("join_")[1]
            async with httpx.AsyncClient() as client2:
                r = await client2.post(
                    f"http://web:80/project/invite/{token}/accept",
                    json={"user_id": user_id},
                )
            if r.status_code == status.HTTP_200_OK:
                await message.answer("🎉 Вы успешно присоединились к проекту!")

        await message.answer(
            f"С возвращением, <b>{user_data['username']}</b>!",
            reply_markup=kb.main_menu,
        )
    else:
        await message.answer(
            "Добро пожаловать!\nДля дальнейшей работы бота <b>нужно пройти регистрацию</b>, для этого пропишите <b>/reg</b> 🎯",
            reply_markup=types.ReplyKeyboardRemove(),
        )


@router.message(Command("about"))
async def about_cmd(message: Message) -> None:
    await message.answer("Тут будет инфо о боте")


@router.message(Command("menu"))
async def main_menu_cmd(message: Message) -> None:
    await message.answer("Главное меню:", reply_markup=kb.main_menu)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.reply("Для перезапуска бота напишите <b>/start</b>")
