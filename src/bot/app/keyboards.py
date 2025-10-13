from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup

get_number = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отправить номер", request_contact=True)]],
    resize_keyboard=True,
)
