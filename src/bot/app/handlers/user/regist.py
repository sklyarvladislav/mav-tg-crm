import app.keyboards as kb
import httpx
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from fastapi import status
from structlog import get_logger

logger = get_logger()
router = Router()


class Reg(StatesGroup):
    name = State()
    number = State()


@router.message(Command("reg"))
async def cmd_reg(message: Message, state: FSMContext) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://web:80/user/{message.from_user.id}"
        )

    if response.status_code == status.HTTP_200_OK:
        user_data = response.json()
        await message.answer(
            f"Вы уже зарегистрированы, <b>{user_data['username']}</b>",
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
    username = data["name"]
    number = data["number"]
    short_name = message.from_user.username

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://web:80/auth",
            json={
                "user_id": user_id,
                "username": username,
                "number": number,
                "short_name": short_name,
            },
            timeout=10.0,
        )

    if response.status_code == status.HTTP_200_OK:
        await message.answer("Успешно!", reply_markup=kb.main_menu)
        logger.info(f"User {username} {user_id} insert into database")
    else:
        await message.answer(
            "Что-то пошло не так, повторите регистрацию еще раз <b>/reg</b>"
        )
        logger.error(f"User {username} {user_id} error reg")

    await state.clear()


@router.message(Command("del"))
async def delete_user_cmd(message: Message) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"http://web:80/user/{message.from_user.id}"
        )

    if response.status_code == status.HTTP_200_OK:
        await message.answer("Ok", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Error")
