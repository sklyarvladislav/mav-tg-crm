import app.keyboards as kb
import httpx
from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from fastapi import status

router = Router()


@router.message(F.text == "🚀 Проекты")
async def project_watch(message: Message) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://web:80/project/owner/{message.from_user.id}"
        )

    if response.status_code == status.HTTP_200_OK:
        projects = response.json()
        keyboard = []

        for project in projects:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=project["name"],
                        callback_data=f"project_{project['project_id']}",
                    )
                ]
            )

        await message.answer(
            "📂 Ваши проекты:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )
        if not projects:
            await message.answer("У вас еще нет проектов")
            return


@router.message(F.text == "⬅️ Главное меню")
async def nazadfromprojects(message: Message) -> None:
    await message.answer("Главное меню", reply_markup=kb.main_menu)
