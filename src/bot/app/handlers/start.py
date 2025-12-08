import app.keyboards as kb
import httpx
from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from fastapi import status

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    text = message.text or ""
    user_id = message.from_user.id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/user/{user_id}")

    if response.status_code == status.HTTP_200_OK:
        user_data = response.json()

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
async def about_command(message: Message) -> None:
    photo_url = "https://i.postimg.cc/59gnGYX9/image-2025-09-28-18-29-25.png"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👤 Алексей", url="https://t.me/lexsik"
                ),
                InlineKeyboardButton(
                    text="👤 Макар", url="https://t.me/W1se_tree"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="👤 Владислав", url="https://t.me/sklyarvlad"
                )
            ],
        ]
    )

    await message.answer_photo(
        photo=photo_url,
        caption=(
            "📋 О сервисе MAV CRM\n\n"
            "Telegram-бот для управления проектами и задачами.\n\n"
            "Возможности:\n"
            "🚀 Создание и управление проектами\n"
            "📝 Управление задачами\n"
            "👥 Работа с участниками\n"
            "📄 Документы и доски\n\n"
            "Используйте /menu для перехода в главное меню"
        ),
        reply_markup=keyboard,
    )


@router.message(Command("menu"))
async def main_menu_cmd(message: Message) -> None:
    await message.answer("Главное меню:", reply_markup=kb.main_menu)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.reply("Для перезапуска бота напишите <b>/start</b>")
