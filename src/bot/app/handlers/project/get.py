import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from fastapi import status
from structlog import get_logger

router = Router()

logger = get_logger()


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


@router.message(F.text == "🚀 Проекты")
async def project_watch(message: Message) -> None:
    logger.info("start find projects")
    await send_projects_list(message)


@router.callback_query(F.data == "back_to_projects")
async def backfromprojects(callback: CallbackQuery) -> None:
    await callback.answer()
    await send_projects_list(
        callback.message, callback.from_user.id, edit=True
    )
