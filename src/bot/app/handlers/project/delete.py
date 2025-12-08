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


async def get_user_role(project_id: str, user_id: int) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"http://web:80/participant/{project_id}/user/{user_id}/role"
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()["role"]
        except Exception:
            pass
    return "USER"


@router.callback_query(F.data.startswith("delete_project_"))
async def delete_confirm(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("delete_project_", "")

    user_role = await get_user_role(project_id, callback.from_user.id)
    if user_role != "OWNER":
        await callback.answer(
            "⛔ Удалять проект может только Владелец!", show_alert=True
        )
        return

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
