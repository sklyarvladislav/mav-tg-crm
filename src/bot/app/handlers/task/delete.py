import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


async def get_user_role(project_id: str, user_id: int) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"http://web:80/participant/{project_id}/user/{user_id}/role"
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()["role"]
        except Exception:
            pass
    return "USER"


@router.callback_query(F.data.startswith("delete_task_"))
async def delete_task(callback: CallbackQuery) -> None:
    task_id = callback.data.replace("delete_task_", "")

    async with httpx.AsyncClient() as client:
        task_response = await client.get(f"http://web:80/task/{task_id}")
        if task_response.status_code != status.HTTP_200_OK:
            await callback.message.edit_text("❌ Ошибка получения задачи")
            return
        task = task_response.json()
        project_id = task["project_id"]
        deleted_number = task.get("number", 0)

        user_role = await get_user_role(project_id, callback.from_user.id)
        if user_role not in ["OWNER", "ADMIN"]:
            await callback.answer(
                "⛔ Удалять задачи могут только админы!", show_alert=True
            )
            return

        delete_response = await client.delete(f"http://web:80/task/{task_id}")
        if delete_response.status_code != status.HTTP_200_OK:
            await callback.message.edit_text("❌ Ошибка удаления задачи")
            return

        tasks_response = await client.get(
            f"http://web:80/task/{project_id}/tasks"
        )
        if tasks_response.status_code == status.HTTP_200_OK:
            tasks = tasks_response.json()
            for t in tasks:
                if t.get("number", 0) > deleted_number:
                    await client.patch(
                        f"http://web:80/task/{t['task_id']}",
                        json={"number": t["number"] - 1},
                    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"get_tasks_{project_id}",
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "✅ Задача удалена", reply_markup=keyboard
    )
