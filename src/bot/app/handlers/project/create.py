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

router = Router()


class MakeProject(StatesGroup):
    project_name = State()
    project_desc = State()
    project_owner = State()


@router.callback_query(F.data == "create_project")
async def make_project(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(MakeProject.project_name)
    await callback.message.answer(
        "Введите название проекта: ", reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(MakeProject.project_name)
async def make_project_name(message: Message, state: FSMContext) -> None:
    await state.update_data(project_name=message.text)
    await state.set_state(MakeProject.project_desc)
    await message.answer("Введите описание проекта: ")


@router.message(MakeProject.project_desc)
async def make_project_desc(message: Message, state: FSMContext) -> None:
    await state.update_data(project_desc=message.text)
    await state.update_data(project_owner=message.from_user.id)

    data = await state.get_data()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://web:80/project",
            json={
                "name": data["project_name"],
                "description": data["project_desc"],
                "status": "В работе",
                "owner": data["project_owner"],
            },
        )

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

    if response.status_code == status.HTTP_200_OK:
        project_data = response.json()
        await message.answer(
            f"✅ Проект создан!\n\n"
            f"Название: {project_data['name']}\n"
            f"Описание: {project_data['description']}\n"
            f"ID: {project_data['project_id']}\n",
            reply_markup=keyboard,
        )
    await state.clear()
