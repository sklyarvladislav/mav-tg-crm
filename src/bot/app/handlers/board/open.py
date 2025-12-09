import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("open_board_"))
async def open_board(callback: CallbackQuery) -> None:
    await callback.answer()
    board_id = callback.data.replace("open_board_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/board/{board_id}")

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить доску")
        return

    board = response.json()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Колонки",
                    callback_data=f"get_columns_{board['board_id']}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🖼️ Kanban",
                    callback_data=f"kanban_{board['board_id']}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="➕ Создать колонку",
                    callback_data=f"create_column_{board['board_id']}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить доску",
                    callback_data=f"delete_board_{board['board_id']}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"get_board_{board['project_id']}",
                )
            ],
        ]
    )

    await callback.message.edit_text(
        f"🗄 Доска:\n\n"
        f"Название: {board['name']}\n"
        f"Количество задачек: {board['number_tasks']}\n"
        f"Позиция: {board['position']}\n",
        reply_markup=keyboard,
    )
