from aiogram import F, Router
from aiogram.types import CallbackQuery
from app.handlers.project.project_info import show_project_screen

router = Router()


@router.callback_query(F.data.startswith("back_to_project_"))
async def back_to_project(callback: CallbackQuery) -> None:
    await callback.answer()
    project_id = callback.data.replace("back_to_project_", "")
    await show_project_screen(callback.message, project_id)
