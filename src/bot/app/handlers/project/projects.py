import app.keyboards as kb
from aiogram import F, Router
from aiogram.types import Message
from app.handlers.project.my_projects import send_projects_list

router = Router()


@router.message(F.text == "🚀 Проекты")
async def project_watch(message: Message) -> None:
    await send_projects_list(message)


@router.message(F.text == "⬅️ Главное меню")
async def backfromprojects(message: Message) -> None:
    await message.answer("Главное меню", reply_markup=kb.main_menu)
