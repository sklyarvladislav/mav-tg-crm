import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from app.handlers.project.info import get_user_role
from fastapi import status
from structlog import get_logger

router = Router()
logger = get_logger()


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery) -> None:
    await callback.answer("У вас нет прав для редактирования участников")


async def send_participants_list(
    message: Message, project_id: str, user_id: int
) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://mav_web:80/participant/{project_id}/participants"
        )

        if response.status_code != status.HTTP_200_OK:
            await message.edit_text("Ошибка получения списка участников")
            return

        participants = response.json()

        role_priority = {"OWNER": 0, "ADMIN": 1, "USER": 2}
        participants.sort(
            key=lambda p: (
                role_priority.get(p.get("role"), 99),
                p.get("user_id"),
            )
        )

        keyboard = []

        viewer_role = await get_user_role(project_id, user_id)

        for p in participants:
            user_response = await client.get(
                f"http://mav_web:80/user/{p['user_id']}"
            )
            if user_response.status_code == status.HTTP_200_OK:
                username = user_response.json().get("username", "Unknown")
            else:
                username = f"User {p['user_id']}"

            role_emoji = {"OWNER": "👑", "ADMIN": "⭐️", "USER": "👤"}
            emoji = role_emoji.get(p["role"], "👤")

            if viewer_role == "USER":
                callback_data = "ignore"
            else:
                callback_data = f"mp_{project_id}_{p['user_id']}"
                if viewer_role == "OWNER":
                    logger.info(
                        f"OWNER CLICK BUTTON: {callback_data} (len={len(callback_data)})"
                    )

            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"{emoji} {username}", callback_data=callback_data
                    )
                ]
            )

    if viewer_role in ["OWNER", "ADMIN"]:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="➕ Добавить участника",
                    callback_data=f"ip_{project_id}",
                )
            ]
        )

    if viewer_role != "OWNER":
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="🚪 Выйти из проекта",
                    callback_data=f"lp_{project_id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"project_{project_id}"
            )
        ]
    )

    await message.edit_text(
        "👥 Участники проекта:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
    )


@router.callback_query(F.data.startswith("get_participant_"))
async def get_participants_handler(callback: CallbackQuery) -> None:
    await callback.answer()
    project_id = callback.data.replace("get_participant_", "")
    await send_participants_list(
        callback.message, project_id, callback.from_user.id
    )
