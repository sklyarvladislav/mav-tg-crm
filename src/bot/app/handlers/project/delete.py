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


@router.callback_query(F.data.startswith("delete_project_"))
async def delete_confirm(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("delete_project_", "")

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить удаление",
                    callback_data=f"confirm_delete_project_{project_id}",
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "❓ Вы уверены?", reply_markup=confirm_keyboard
    )


@router.callback_query(F.data.startswith("confirm_delete_project_"))
async def delete_project(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("confirm_delete_project_", "")

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://web:80/project/{project_id}")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к проектам",
                    callback_data="back_to_projects",
                )
            ]
        ]
    )

    if response.status_code == status.HTTP_200_OK:
        await callback.message.edit_text(
            "✅ Проект удален", reply_markup=keyboard
        )
    else:
        await callback.message.edit_text("❌ Ошибка")
