import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("delete_doc_"))
async def delete_document(callback: CallbackQuery) -> None:
    document_id = callback.data.replace("delete_doc_", "")

    async with httpx.AsyncClient() as client:
        doc_response = await client.get(
            f"http://web:80/document/{document_id}"
        )

        if doc_response.status_code == status.HTTP_200_OK:
            doc = doc_response.json()
            project_id = doc["project_id"]

            response = await client.delete(
                f"http://web:80/document/{document_id}"
            )

            if response.status_code == status.HTTP_200_OK:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="⬅️ Назад",
                                callback_data=f"get_doc_{project_id}",
                            )
                        ]
                    ]
                )
                await callback.message.edit_text(
                    "✅ Документ удален", reply_markup=keyboard
                )
            else:
                await callback.message.edit_text(
                    "❌ Ошибка удаления документа"
                )
