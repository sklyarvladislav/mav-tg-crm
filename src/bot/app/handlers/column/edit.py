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


class EditColumn(StatesGroup):
    column_name = State()


@router.callback_query(F.data.startswith("edit_column_"))
async def start_edit_column(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await callback.answer()

    column_id = callback.data.replace("edit_column_", "")

    # Get current column info
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/column/{column_id}")

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить колонку")
        return

    column = response.json()

    await state.update_data(column_id=column_id, board_id=column["board_id"])
    await state.set_state(EditColumn.column_name)
    await callback.message.answer(
        f"Текущее название: {column['name']}\n\n"
        "Введите новое название колонки:"
    )


@router.message(EditColumn.column_name)
async def edit_column_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    column_id = data["column_id"]
    new_name = message.text

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"http://web:80/column/{column_id}",
            json={"name": new_name},
        )

    if response.status_code == status.HTTP_200_OK:
        column = response.json()
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад к колонке",
                        callback_data=f"open_column_{column_id}",
                    )
                ]
            ]
        )
        await message.answer(
            f"✅ Название колонки обновлено!\n\n"
            f"Новое название: {column['name']}",
            reply_markup=keyboard,
        )
    else:
        await message.answer("❌ Ошибка при обновлении колонки")

    await state.clear()
