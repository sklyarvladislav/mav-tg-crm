import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("get_tasks_"))
async def show_boards(callback: CallbackQuery) -> None:
    await callback.answer()

    project_id = callback.data.replace("get_tasks_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/task/{project_id}/tasks")

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить таски")
        return

    tasks = response.json()

    keyboard_buttons = [
        [
            InlineKeyboardButton(
                text=f" 🗄 {task['name']}",
                callback_data=f"open_task_{task['task_id']}",
            )
        ]
        for task in tasks
    ]
    keyboard_buttons.append(
        [
            InlineKeyboardButton(
                text="➕ Создать таску",
                callback_data=f"create_task_{project_id}",
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

    await callback.message.edit_text("🗄 Таски проекта:", reply_markup=keyboard)
