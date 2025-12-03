import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("open_task_"))
async def open_task(callback: CallbackQuery) -> None:
    await callback.answer()
    task_id = callback.data.replace("open_task_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/task/{task_id}")

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить задачу")
        return

    task = response.json()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить задачу",
                    callback_data=f"delete_task_{task['task_id']}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"get_tasks_{task['project_id']}",
                )
            ],
        ]
    )

    document_link = None
    if task.get("document_id"):
        async with httpx.AsyncClient() as client:
            doc_resp = await client.get(
                f"http://web:80/document/{task['document_id']}"
            )
        if doc_resp.status_code == status.HTTP_200_OK:
            document = doc_resp.json()
            document_link = document.get("link")

    await callback.message.edit_text(
        f"📝 Задача:\n\n"
        f"Название: {task['name']}\n"
        f"Описание: {task['text']}\n"
        f"Медиа: {document_link or 'Нет'}\n"
        f"Исполнитель: {task['user_id']}\n"
        f"Статус: {task['status']}\n"
        f"Приоритет: {task['priority']}\n"
        f"Дедлайн: {task['deadline']}\n",
        reply_markup=keyboard,
    )
