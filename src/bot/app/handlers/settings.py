import app.keyboards as kb
import httpx
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from fastapi import status

router = Router()


class Settings(StatesGroup):
    new_name = State()


@router.message(F.text == "⚙️ Настройки")
async def settings_menu(message: Message) -> None:
    await message.answer(
        "Настройки <b>профиля</b>:", reply_markup=kb.settings_menu
    )


@router.message(F.text == "✏️ Изменить имя")
async def change_name_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Settings.new_name)
    await message.answer(
        "Введите новое <b>имя</b>:", reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(Settings.new_name)
async def change_name_finish(message: Message, state: FSMContext) -> None:
    new_name = message.text

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            f"http://web:80/user/{message.from_user.id}"
        )
        user_data = user_response.json()
        user_data["username"] = new_name

        response = await client.patch(
            f"http://web:80/user/{message.from_user.id}", json=user_data
        )

    if response.status_code == status.HTTP_200_OK:
        await message.answer(
            "Имя <b>успешно</b> изменено!", reply_markup=kb.settings_menu
        )
    else:
        await message.answer("Ошибка изменения имени")

    await state.clear()
