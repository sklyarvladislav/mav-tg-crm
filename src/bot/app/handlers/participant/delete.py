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


@router.callback_query(F.data.startswith("delpart_"))
async def delete_participant(callback: CallbackQuery) -> None:
    await callback.answer()
    _, project_id, user_id = callback.data.split("_")
    logger.info(f"{project_id} nd {user_id}")
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"http://web:80/participant/{project_id}/{user_id}"
        )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"get_participant_{project_id}",
                )
            ],
        ]
    )

    if resp.status_code == status.HTTP_200_OK:
        await callback.message.edit_text(
            "✅ Участник удалён", reply_markup=keyboard
        )
    else:
        await callback.message.edit_text("❌ Ошибка удаления")
