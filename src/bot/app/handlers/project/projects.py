import app.keyboards as kb
from aiogram import F, Router
from aiogram.types import Message

router = Router()


@router.message(F.text == "🚀 Проекты")
async def project_watch(message: Message) -> None:
    await message.answer("Ваши проекты:", reply_markup=kb.projects_menu)


@router.message(F.text == "⬅️ Главное меню")
async def nazadfromprojects(message: Message) -> None:
    await message.answer("Главное меню", reply_markup=kb.main_menu)
