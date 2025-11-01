from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup

get_number = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отправить номер", request_contact=True)]],
    resize_keyboard=True,
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Проекты")],
        [
            KeyboardButton(text="👤 Профиль"),
            KeyboardButton(text="⚙️ Настройки"),
        ],
    ],
    resize_keyboard=True,
)

back_from_profile = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⬅️ Назад")]], resize_keyboard=True
)

settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✏️ Изменить имя")],
        [KeyboardButton(text="⬅️ Назад")],
    ],
    resize_keyboard=True,
)
