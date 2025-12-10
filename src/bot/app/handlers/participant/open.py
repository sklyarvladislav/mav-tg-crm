import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status
from structlog import get_logger

logger = get_logger()
router = Router()


@router.callback_query(F.data.startswith("open_participant_"))
async def open_participant(callback: CallbackQuery) -> None:
    await callback.answer()
    logger.info(callback.data.split("_"))
    _, _, project_id, user_id = callback.data.split("_")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/user/{user_id}")

        resp_part = await client.get(
            f"http://web:80/participant/{project_id}/participants"
        )

    participants = resp_part.json()

    participant_data = next(
        (p for p in participants if p["user_id"] == int(user_id)), None
    )

    if not participant_data:
        await callback.message.answer("❌ Участник не найден в проекте")
        return

    role = participant_data["role"]

    if response.status_code == status.HTTP_200_OK:
        participant = response.json()
        logger.info(participant)
        username = participant.get("short_name", "unknown")
        name = participant.get("username", username)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔑 Поменять роль",
                        callback_data=f"change_participant_{participant['user_id']}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Исключить участника",
                        callback_data=f"delpart_{project_id}_{user_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=f"get_participant_{project_id}",
                    )
                ],
            ]
        )

        await callback.message.edit_text(
            f"👤 <b>{name}</b> (@{username})\n"
            f"🆔 ID: {user_id}\n"
            f"🔑 Роль: <b>{role}</b>",
            reply_markup=keyboard,
        )
