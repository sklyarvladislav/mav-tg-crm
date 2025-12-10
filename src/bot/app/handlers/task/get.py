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
async def show_tasks(callback: CallbackQuery) -> None:
    await callback.answer()
    project_id = callback.data.replace("get_tasks_", "")
    current_user_id = callback.from_user.id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/task/{project_id}/tasks")

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить задачи")
        return

    tasks = response.json()

    tasks.sort(key=lambda x: x.get("number", 0))

    priority_emoji = {
        "WITHOUT": "⚪",
        "LOW": "🟢",
        "MEDIUM": "🟡",
        "HIGH": "🔴",
        "FROZEN": "🧊",
    }

    keyboard_buttons = []

    for task in tasks:
        p_emoji = priority_emoji.get(task.get("priority", "WITHOUT"), "⚪")

        me_mark = (
            " (Исполнитель)" if task.get("user_id") == current_user_id else ""
        )

        btn_text = f"{p_emoji} {task['name']}{me_mark}"

        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"open_task_{task['task_id']}",
                )
            ]
        )

    keyboard_buttons.append(
        [
            InlineKeyboardButton(
                text="➕ Создать задачу",
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

    await callback.message.edit_text(
        "📝 Задачи проекта:", reply_markup=keyboard
    )
