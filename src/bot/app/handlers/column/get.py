import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("get_columns_"))
async def get_columns(callback: CallbackQuery) -> None:
    await callback.answer()
    board_id = callback.data.replace("get_columns_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/column/{board_id}/columns")

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить колонки")
        return

    columns = response.json()

    # Get board info
    async with httpx.AsyncClient() as client:
        board_response = await client.get(f"http://web:80/board/{board_id}")
    
    if board_response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить доску")
        return
    
    board = board_response.json()

    # Get task counts for each column
    async with httpx.AsyncClient() as client:
        tasks_response = await client.get(f"http://web:80/task/{board['project_id']}/tasks")
    
    task_counts = {}
    if tasks_response.status_code == status.HTTP_200_OK:
        tasks = tasks_response.json()
        for task in tasks:
            if task.get("column_id"):
                column_id = task["column_id"]
                task_counts[column_id] = task_counts.get(column_id, 0) + 1

    keyboard = []
    
    if columns:
        for column in columns:
            task_count = task_counts.get(column["column_id"], 0)
            keyboard.append([
                InlineKeyboardButton(
                    text=f"📋 {column['name']} ({task_count})",
                    callback_data=f"open_column_{column['column_id']}",
                )
            ])
    else:
        keyboard.append([
            InlineKeyboardButton(
                text="📋 Колонок пока нет",
                callback_data="no_columns",
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="➕ Создать колонку",
            callback_data=f"create_column_{board_id}",
        )
    ])
    keyboard.append([
        InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"open_board_{board_id}",
        )
    ])

    await callback.message.edit_text(
        f"📋 Колонки доски: {board['name']}\n\n"
        f"Количество колонок: {len(columns)}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )
