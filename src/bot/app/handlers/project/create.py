import httpx
from aiogram import F, Router, types
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


class MakeProject(StatesGroup):
    project_name = State()
    project_desc = State()


@router.callback_query(F.data == "create_project")
async def make_project(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(MakeProject.project_name)
    await callback.message.answer(
        "Введите название проекта:", reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(MakeProject.project_name)
async def make_project_name(message: Message, state: FSMContext) -> None:
    await state.update_data(project_name=message.text)
    await state.set_state(MakeProject.project_desc)
    await message.answer("Введите описание проекта:")


@router.message(MakeProject.project_desc)
async def make_project_desc(message: Message, state: FSMContext) -> None:
    await state.update_data(project_desc=message.text)
    user_id = message.from_user.id

    data = await state.get_data()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://web:80/project?user_id={user_id}",
            json={
                "name": str(data["project_name"]),
                "description": str(data["project_desc"]),
                "status": "В работе",
            },
        )

    if response.status_code != status.HTTP_200_OK:
        await message.answer("❌ Ошибка при создании проекта")
        await state.clear()
        return

    project_data = response.json()
    project_id = project_data["project_id"]

    # 3️⃣ Клавиатура возврата
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к проектам",
                    callback_data="back_to_projects",
                )
            ]
        ]
    )

    await message.answer(
        f"✅ Проект создан!\n\n"
        f"Название: {project_data['name']}\n"
        f"Описание: {project_data['description']}\n"
        f"ID: {project_id}",
        reply_markup=keyboard,
    )

    await state.clear()
