from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup

get_number = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отправить номер", request_contact=True)]],
    resize_keyboard=True,
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Профиль")],
        [KeyboardButton(text="Кнопка1"), KeyboardButton(text="Кнопка2")],
    ],
    resize_keyboard=True,
)

back_from_profile = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⬅️ Назад")]], resize_keyboard=True
)
