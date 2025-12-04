import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status
from structlog import get_logger

router = Router()
logger = get_logger()


@router.callback_query(F.data.startswith("get_participant_"))
async def show_participant(callback: CallbackQuery) -> None:
    await callback.answer()

    project_id = callback.data.replace("get_participant_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://web:80/participant/{project_id}/participants"
        )

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer(
            "❌ Не удалось получить список участников"
        )
        return

    participants = response.json()
    logger.info(participants)

    # Получаем имена участников
    async with httpx.AsyncClient() as client:
        for participant in participants:
            user_resp = await client.get(
                f"http://web:80/user/{participant['user_id']}"
            )
            if user_resp.status_code == status.HTTP_200_OK:
                user_data = user_resp.json()
                logger.info(user_data)
                # Берём username вместо несуществующего name
                participant["name"] = user_data.get(
                    "username", f"User {participant['user_id']}"
                )
            else:
                participant["name"] = f"User {participant['user_id']}"

    keyboard_buttons = [
        [
            InlineKeyboardButton(
                text=f"👤 {participant['name']}",
                callback_data=f"open_participant_{project_id}_{participant['user_id']}",
            )
        ]
        for participant in participants
        if participant["role"] != "OWNER"
    ]

    keyboard_buttons.append(
        [
            InlineKeyboardButton(
                text="➕ Добавить участника",
                callback_data=f"invite_{project_id}",
            )
        ]
    )
    keyboard_buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"project_{project_id}"
            )
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.message.edit_text(
        "👥 Участники проекта:", reply_markup=keyboard
    )
