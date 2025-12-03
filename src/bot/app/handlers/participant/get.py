import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("get_participant_"))
async def show_documents(callback: CallbackQuery) -> None:
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

    keyboard_buttons = [
        [
            InlineKeyboardButton(
                text=f"📄 {participant['user_id']}",
                callback_data=f"open_participant_{participant['user_id']}",
            )
        ]
        for participant in participants
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
                text="⬅️ Назад",
                callback_data=f"project_{project_id}",
            )
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.message.edit_text(
        "👥 Участники проекта:", reply_markup=keyboard
    )
