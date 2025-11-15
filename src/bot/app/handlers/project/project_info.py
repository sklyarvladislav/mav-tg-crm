import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("project_"))
async def project_details(callback: CallbackQuery) -> None:
    await callback.answer()
    project_id = callback.data.replace("project_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/project/{project_id}")

    if response.status_code == status.HTTP_200_OK:
        project = response.json()

        async with httpx.AsyncClient() as client2:
            user_response = await client2.get(
                f"http://web:80/user/{project['owner']}"
            )
            owner_name = (
                user_response.json()["username"]
                if user_response.status_code == status.HTTP_200_OK
                else "ошибка получения имени :("
            )

        settings_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⚙️ Настроить",
                        callback_data=f"settings_{project_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="➕ Создать документ",
                        callback_data=f"create_doc_{project_id}",
                    )
                ],
            ]
        )

        await callback.message.answer(
            f"📋 <b>{project['name']}</b>\n\n"
            f"Описание: {project['description']}\n"
            f"ID: {project['project_id']}\n"
            f"Владелец: {owner_name}",
            reply_markup=settings_keyboard,
        )
    else:
        await callback.message.answer("Проект не найден")
