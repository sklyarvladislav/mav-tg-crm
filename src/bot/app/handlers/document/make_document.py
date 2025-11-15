import httpx
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from fastapi import status

router = Router()


class MakeDocument(StatesGroup):
    document_name = State()
    document_link = State()


@router.callback_query(F.data.startswith("create_doc_"))
async def start_create_document(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await callback.answer()

    project_id = callback.data.replace("create_doc_", "")
    await state.update_data(project_id=project_id)

    await state.set_state(MakeDocument.document_name)
    await callback.message.answer("Введите название документа:")


@router.message(MakeDocument.document_name)
async def document_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(MakeDocument.document_link)
    await message.answer("Отправьте ссылку на документ:")


@router.message(MakeDocument.document_link)
async def document_link(message: Message, state: FSMContext) -> None:
    await state.update_data(link=message.text)

    data = await state.get_data()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://web:80/document",
            json={
                "name": data["name"],
                "link": data["link"],
                "project_id": data["project_id"],
            },
        )

    if response.status_code == status.HTTP_200_OK:
        doc = response.json()
        await message.answer(
            f"📄 Документ создан!\n\n"
            f"Название: {doc['name']}\n"
            f"Ссылка: {doc['link']}\n"
            f"ID документа: {doc['document_id']}\n"
            f"Прикреплён к проекту: {doc['project_id']}",
            disable_web_page_preview=True,
        )
    else:
        await message.answer("❌ Ошибка при создании документа")

    await state.clear()
