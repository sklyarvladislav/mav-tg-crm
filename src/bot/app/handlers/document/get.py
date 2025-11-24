import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("get_doc_"))
async def show_documents(callback: CallbackQuery) -> None:
    """
    При нажатии на кнопку 📄 Документы показывает список документов проекта.
    """
    await callback.answer()  # чтобы Telegram не показывал "loading..."

    project_id = callback.data.replace("get_doc_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://web:80/document/{project_id}/documents"
        )

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить документы")
        return

    documents = response.json()
    if not documents:
        await callback.message.answer("📂 Документов пока нет")
        return

    # формируем клавиатуру
    keyboard_buttons = [
        [
            InlineKeyboardButton(
                text=f"📄 {doc['name']}",
                callback_data=f"open_doc_{doc['document_id']}",
            )
        ]
        for doc in documents
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.message.answer(
        "📂 Список документов:", reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("open_doc_"))
async def open_document(callback: CallbackQuery) -> None:
    """
    Хендлер для открытия конкретного документа по кнопке.
    """
    await callback.answer()
    document_id = callback.data.replace("open_doc_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/document/{document_id}")

    if response.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить документ")
        return

    doc = response.json()
    await callback.message.answer(
        f"📄 Документ:\n\n"
        f"Название: {doc['name']}\n"
        f"Ссылка: {doc['link']}\n"
        f"ID документа: {doc['document_id']}",
        disable_web_page_preview=True,
    )
