import app.keyboards as kb
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from app.handlers.start import user_bd

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
    user_bd[message.from_user.id] = {
        "name": data["name"],
        "number": data["number"],
    }
    await message.answer(
        "Успешно!",
        reply_markup=kb.main_menu,
    )
    await state.clear()
