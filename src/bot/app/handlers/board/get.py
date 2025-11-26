import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("get_board_"))
async def show_boards(callback: CallbackQuery) -> None:
    await callback.answer()

    project_id = callback.data.replace("get_board_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/board/{project_id}/boards")

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить доски")
        return

    boards = response.json()

    keyboard_buttons = [
        [
            InlineKeyboardButton(
                text=f"📄 {board['name']}",
                callback_data=f"open_board_{board['board_id']}",
            )
        ]
        for board in boards
    ]
    keyboard_buttons.append(
        [
            InlineKeyboardButton(
                text="➕ Создать доску",
                callback_data=f"create_board_{project_id}",
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

    await callback.message.edit_text("🗄 Доски проекта:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("open_board_"))
async def open_board(callback: CallbackQuery) -> None:
    """
    Хендлер для открытия конкретного документа по кнопке.
    """
    await callback.answer()
    board_id = callback.data.replace("open_board_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/board/{board_id}")

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить доску")
        return

    board = response.json()
    await callback.message.edit_text(
        f"🗄 Доска:\n\n"
        f"Название: {board['name']}\n"
        f"Количество задачек: {board['number_tasks']}\n"
    )
