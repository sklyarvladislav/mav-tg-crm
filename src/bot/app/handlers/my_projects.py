import httpx
from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from fastapi import status

router = Router()


@router.message(F.text == "📋 Мои проекты")
async def my_projects(message: Message) -> None:
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
    else:
        await message.answer("У вас еще нет проектов")
