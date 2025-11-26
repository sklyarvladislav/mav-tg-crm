import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from fastapi import status

router = Router()


async def show_project_screen(message: Message, project_id: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/project/{project_id}")

    if response.status_code != status.HTTP_200_OK:
        await message.edit_text("❌ Проект не найден")
        return

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

    keyboard_buttons = [
        [
            InlineKeyboardButton(
                text="⚙️ Настроить", callback_data=f"settings_{project_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📄 Документы", callback_data=f"get_doc_{project_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📁 Доски", callback_data=f"get_board_{project_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📝 Таски", callback_data=f"get_tasks_{project_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="👥 Участники", callback_data=f"get_users_{project_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data="back_to_projects"
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await message.edit_text(
        f"📋 <b>{project['name']}</b>\n\n"
        f"Описание: {project['description']}\n"
        f"Статус: {project['status']}\n"
        f"ID: {project['project_id']}\n"
        f"Владелец: {owner_name}",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("project_"))
async def project_details(callback: CallbackQuery) -> None:
    await callback.answer()
    project_id = callback.data.replace("project_", "")
    await show_project_screen(callback.message, project_id)
