import httpx
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from fastapi import status

router = Router()


class MakeColumn(StatesGroup):
    column_name = State()


@router.callback_query(F.data.startswith("create_column_"))
async def start_create_column(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await callback.answer()

    board_id = callback.data.replace("create_column_", "")
    await state.update_data(board_id=board_id)

    await state.set_state(MakeColumn.column_name)
    await callback.message.answer("Введите название колонки:")


@router.message(MakeColumn.column_name)
async def column_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    board_id = data["board_id"]
    column_name = message.text

    # Get existing columns to calculate position
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/column/{board_id}/columns")

    if response.status_code == status.HTTP_200_OK:
        columns = response.json()
        if columns:
            max_position = max(column["position"] for column in columns)
            position = max_position + 1
        else:
            position = 1
    else:
        position = 1

    # Create column
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://web:80/column",
            json={
                "name": column_name,
                "board_id": str(board_id),
                "position": position,
            },
        )

    if response.status_code == status.HTTP_200_OK:
        column = response.json()
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад к колонкам", 
                        callback_data=f"get_columns_{board_id}"
                    )
                ]
            ]
        )
        await message.answer(
            f"📋 Колонка создана!\n\n"
            f"Название: {column['name']}\n"
            f"ID колонки: {column['column_id']}\n"
            f"Позиция: {column['position']}",
            reply_markup=keyboard,
        )
    else:
        await message.answer("❌ Ошибка при создании колонки")

    await state.clear()
