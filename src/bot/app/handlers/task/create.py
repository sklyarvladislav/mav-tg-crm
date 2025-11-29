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
from structlog import get_logger

router = Router()
logger = get_logger()


class MakeTask(StatesGroup):
    task_name = State()
    task_document = State()


@router.callback_query(F.data.startswith("create_task_"))
async def start_create_task(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await callback.answer()

    project_id = callback.data.replace("create_task_", "")

    await state.update_data(project_id=project_id)

    await state.set_state(MakeTask.task_name)
    await callback.message.answer("Введите название задачки:")


@router.message(MakeTask.task_name)
async def board_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    project_id = data["project_id"]
    board_name = message.text

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/board/{project_id}/boards")

    if response.status_code == status.HTTP_200_OK:
        boards = response.json()
        logger.info(boards)
        if boards:
            max_position = max(board["position"] for board in boards)
            position = max_position + 1
        else:
            position = 0
    else:
        position = 0

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://web:80/board",
            json={
                "name": board_name,
                "project_id": str(project_id),
                "position": position,
                "number_tasks": 0,
            },
        )

    if response.status_code == status.HTTP_200_OK:
        board = response.json()
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад", callback_data=f"get_board_{project_id}"
                    )
                ]
            ]
        )
        await message.answer(
            f"🗄Доска создана!\n\nНазвание: {board['name']}\nID доски: {board['board_id']}\nТекущая позиция: {board['position']}",
            reply_markup=keyboard,
        )
    else:
        await message.answer("❌ Ошибка при создании доски")

    await state.clear()
