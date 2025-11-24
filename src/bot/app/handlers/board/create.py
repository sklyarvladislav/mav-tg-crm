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


class MakeBoard(StatesGroup):
    board_name = State()
    board_description = State()


@router.callback_query(F.data.startswith("create_board_"))
async def start_create_board(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """
    Старт процесса создания доски.
    Устанавливает проект и переводит FSM в состояние ввода названия доски.
    """
    await callback.answer()

    project_id = callback.data.replace("create_board_", "")
    await state.update_data(project_id=project_id)

    await state.set_state(MakeBoard.board_name)
    await callback.message.answer("Введите название доски:")


@router.message(MakeBoard.board_name)
async def board_name(message: Message, state: FSMContext) -> None:
    """
    Сохраняет название доски и переводит FSM в состояние ввода описания.
    """
    await state.update_data(name=message.text)
    await state.set_state(MakeBoard.board_description)
    await message.answer("Введите описание доски:")


@router.message(MakeBoard.board_description)
async def board_description(message: Message, state: FSMContext) -> None:
    await state.update_data(
        description=message.text
    )  # можно оставить для информации

    data = await state.get_data()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://web:80/board",
            json={
                "name": data["name"],
                "project_id": str(data["project_id"]),
                "position": 0,
                "number_tasks": 0,
            },
        )

    if response.status_code == status.HTTP_200_OK:
        board = response.json()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад к проекту",
                        callback_data=f"project_{board['project_id']}",
                    )
                ]
            ]
        )

        await message.answer(
            f"📋 Доска создана!\n\n"
            f"Название: {board['name']}\n"
            f"ID доски: {board['board_id']}",
            reply_markup=keyboard,
        )
    else:
        await message.answer("❌ Ошибка при создании доски")

    await state.clear()
