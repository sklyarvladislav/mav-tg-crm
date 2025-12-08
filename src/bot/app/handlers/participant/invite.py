import urllib.parse

import httpx
from aiogram import F, Router, html
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("ip_"))
async def invite(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("ip_", "")

    try:
        async with httpx.AsyncClient() as client:
            project_resp = await client.get(
                f"http://web:80/project/{project_id}"
            )
            project_name = "проект"
            if project_resp.status_code == status.HTTP_200_OK:
                project_data = project_resp.json()
                project_name = project_data.get("name", "проект")

            r = await client.post(f"http://web:80/project/{project_id}/invite")
            r.raise_for_status()
            token = r.json().get("token")

            if not token:
                return

            bot_info = await callback.bot.get_me()

            invite_url = f"https://t.me/{bot_info.username}?start=join_{token}"

            share_url = (
                f"https://t.me/share/url?url={urllib.parse.quote(invite_url)}"
            )

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📨 Отправить", url=share_url)],
                    [
                        InlineKeyboardButton(
                            text="⬅️ Назад",
                            callback_data=f"get_participant_{project_id}",
                        )
                    ],
                ]
            )

            await callback.message.edit_text(
                f"🔗 <b>Приглашение в проект «{project_name}»</b>\n\n"
                f"Ссылка для вступления:\n{html.code(invite_url)}",
                reply_markup=keyboard,
                parse_mode="HTML",
            )

    except Exception as e:
        await callback.message.answer(f"Ошибка: {e}")
