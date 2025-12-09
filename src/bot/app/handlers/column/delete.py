import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("delete_column_"))
async def delete_column(callback: CallbackQuery) -> None:
    await callback.answer()
    column_id = callback.data.replace("delete_column_", "")

    # Get column info to get board_id
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/column/{column_id}")
    
    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить колонку")
        return
    
    column = response.json()
    board_id = column["board_id"]

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://web:80/column/{column_id}")

    if response.status_code == status.HTTP_200_OK:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад к колонкам",
                        callback_data=f"get_columns_{board_id}",
                    )
                ]
            ]
        )
        await callback.message.edit_text(
            f"✅ Колонка удалена!\n\n"
            f"Название: {column['name']}",
            reply_markup=keyboard,
        )
    else:
        await callback.message.answer("❌ Ошибка при удалении колонки")
