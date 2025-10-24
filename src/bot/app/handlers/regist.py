import app.keyboards as kb
import httpx
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from app.handlers.start import user_bd
from fastapi import status
from structlog import get_logger

logger = get_logger()
router = Router()


class Reg(StatesGroup):
    name = State()
    number = State()


@router.message(Command("reg"))
async def cmd_reg(message: Message, state: FSMContext) -> None:
    if message.from_user.id in user_bd:
        await message.answer(
            f"Вы уже зарегестрированы, <b>{user_bd[message.from_user.id]['name']}</b>",
            reply_markup=kb.main_menu,
        )
    else:
        await state.set_state(Reg.name)
        await message.answer("Введите ваше <b>имя</b>")


@router.message(Reg.name)
async def reg_two(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Reg.number)
    await message.answer(
        "Отправьте ваш номер телефона", reply_markup=kb.get_number
    )


@router.message(Reg.number, F.contact)
async def reg_three(message: Message, state: FSMContext) -> None:
    await state.update_data(number=message.contact.phone_number)
    data = await state.get_data()

    user_id = message.from_user.id
    username = message.from_user.username or f"user{user_id}"
    number = data["number"]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://web:80/api/auth",
            json={"user_id": user_id, "username": username, "number": number},
            timeout=10.0,
        )

    if response.status_code == status.HTTP_200_OK:
        await message.answer("Success!", reply_markup=kb.main_menu)
        logger.info("User insert into database")
    else:
        await message.answer("Error... try later...")

    await state.clear()
