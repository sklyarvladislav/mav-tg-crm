from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from app.handlers.project.my_projects import send_projects_list

router = Router()


@router.message(F.text == "🚀 Проекты")
async def project_watch(message: Message) -> None:
    await send_projects_list(message)


@router.callback_query(F.data == "back_to_projects")
async def backfromprojects(callback: CallbackQuery) -> None:
    await callback.answer()
    await send_projects_list(
        callback.message, callback.from_user.id, edit=True
    )
