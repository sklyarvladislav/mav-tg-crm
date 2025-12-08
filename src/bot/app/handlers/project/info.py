import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from fastapi import status
from structlog import get_logger

router = Router()
logger = get_logger()


async def get_user_role(project_id: str, user_id: int) -> str:
    """Получает роль пользователя через новый endpoint"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://web:80/participant/{project_id}/user/{user_id}/role"
        )

        if response.status_code == status.HTTP_200_OK:
            return response.json()["role"]
        return "USER"


async def show_project_screen(
    message: Message, project_id: str, user_id: int
) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/project/{project_id}")

        if response.status_code != status.HTTP_200_OK:
            await message.edit_text("❌ Проект не найден")
            return

        project = response.json()

    owner_name = "Неизвестен"
    async with httpx.AsyncClient() as client2:
        participants_resp = await client2.get(
            f"http://web:80/participant/{project_id}/participants"
        )

        if participants_resp.status_code == status.HTTP_200_OK:
            participants = participants_resp.json()
            owner = next(
                (p for p in participants if p["role"] == "OWNER"), None
            )

            if owner:
                user_resp = await client2.get(
                    f"http://web:80/user/{owner['user_id']}"
                )
                if user_resp.status_code == status.HTTP_200_OK:
                    owner_name = user_resp.json().get("username", "Неизвестен")

    user_role = await get_user_role(project_id, user_id)

    keyboard_buttons = []

    if user_role in ["OWNER", "ADMIN"]:
        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text="⚙️ Настроить", callback_data=f"settings_{project_id}"
                )
            ]
        )

    keyboard_buttons.extend(
        [
            [
                InlineKeyboardButton(
                    text="📄 Документы", callback_data=f"get_doc_{project_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗄 Доски", callback_data=f"get_board_{project_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Задачи", callback_data=f"get_tasks_{project_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Участники",
                    callback_data=f"get_participant_{project_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data="back_to_projects"
                )
            ],
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    role_emoji = {
        "OWNER": "👑 Владелец",
        "ADMIN": "⭐️ Админ",
        "USER": "👤 Участник",
    }

    role_text = role_emoji.get(user_role, user_role)

    await message.edit_text(
        f"📋 <b>{project['name']}</b>\n\n"
        f"📝 {project['description']}\n"
        f"Статус: {project['status']}\n"
        f"Владелец: {owner_name}\n"
        f"Ваша роль: {role_text}",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("project_"))
async def project_details(callback: CallbackQuery) -> None:
    await callback.answer()
    project_id = callback.data.replace("project_", "")

    await show_project_screen(
        callback.message, project_id, callback.from_user.id
    )
