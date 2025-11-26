import httpx
from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from fastapi import status

router = Router()


async def send_projects_list(
    message: Message, user_id: int | None = None, edit: bool = False
) -> None:
    if user_id is None and message is not None:
        user_id = message.from_user.id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/project/owner/{user_id}")

    if response.status_code != status.HTTP_200_OK:
        await message.answer("Не удалось получить список проектов")
        return

    projects = response.json()
    keyboard = []

    for project in projects:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=project["name"],
                    callback_data=f"project_{project['project_id']}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="➕ Создать проект", callback_data="create_project"
            )
        ]
    )

    if edit:
        await message.edit_text(
            "📂 Ваши проекты:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )
    else:
        await message.answer(
            "📂 Ваши проекты:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )
