import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("open_column_"))
async def open_column(callback: CallbackQuery) -> None:
    await callback.answer()
    column_id = callback.data.replace("open_column_", "")

    async with httpx.AsyncClient() as client:
        # Get column info
        response = await client.get(f"http://web:80/column/{column_id}")

        if response.status_code != status.HTTP_200_OK:
            await callback.message.answer("❌ Не удалось получить колонку")
            return

        column = response.json()
        board_id = column["board_id"]

        # Get board info
        board_response = await client.get(f"http://web:80/board/{board_id}")
        
        if board_response.status_code != status.HTTP_200_OK:
            await callback.message.answer("❌ Не удалось получить доску")
            return
        
        board = board_response.json()

        # Get task count for this column
        tasks_response = await client.get(f"http://web:80/task/{board['project_id']}/tasks")
        
        task_count = 0
        if tasks_response.status_code == status.HTTP_200_OK:
            tasks = tasks_response.json()
            task_count = sum(1 for task in tasks if task.get("column_id") == column_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Изменить название",
                    callback_data=f"edit_column_{column['column_id']}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить колонку",
                    callback_data=f"delete_column_{column['column_id']}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"get_columns_{board_id}",
                )
            ],
        ]
    )

    await callback.message.edit_text(
        f"📋 Колонка:\n\n"
        f"Название: {column['name']}\n"
        f"Количество задач: {task_count}\n"
        f"Позиция: {column['position']}\n",
        reply_markup=keyboard,
    )
