import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("open_doc_"))
async def open_document(callback: CallbackQuery) -> None:
    await callback.answer()
    document_id = callback.data.replace("open_doc_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/document/{document_id}")

    if response.status_code == status.HTTP_200_OK:
        doc = response.json()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🗑️ Удалить документ",
                        callback_data=f"delete_doc_{doc['document_id']}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=f"get_doc_{doc['project_id']}",
                    )
                ],
            ]
        )

        await callback.message.edit_text(
            f"📄 <b>{doc['name']}</b>\n\n"
            f"Ссылка: {doc['link']}\n"
            f"ID: {doc['document_id']}",
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
