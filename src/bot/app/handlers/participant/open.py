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
    participant_id = callback.data.replace("open_participant_", "")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://web:80/participant/{participant_id}"
        )

    if response.status_code == status.HTTP_200_OK:
        participant = response.json()

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
                        callback_data=f"delete_participant_{participant['user_id']}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=f"get_participant_{participant['project_id']}",
                    )
                ],
            ]
        )

        await callback.message.answer(
            f"📄 <b>{participant['user_id']}</b>\n\n"
            f"username is not found {participant_id}",
            reply_markup=keyboard,
        )
