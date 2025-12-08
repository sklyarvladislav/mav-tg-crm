import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

router = Router()


@router.callback_query(F.data.startswith("ip_"))
async def invite(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("ip_", "")

    try:
        # создаем токен на сервере
        async with httpx.AsyncClient() as client:
            r = await client.post(f"http://web:80/project/{project_id}/invite")
            r.raise_for_status()  # проверяем успешность запроса

        data = r.json()
        token = data.get("token")
        if not token:
            await callback.message.answer("❌ Не удалось создать приглашение.")
            return

        bot_info = await callback.bot.get_me()
        bot_username = bot_info.username
        ip_link = f"https://t.me/{bot_username}?start=join_{token}"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=f"get_participant_{project_id}",
                    )
                ]
            ]
        )

        await callback.message.edit_text(
            "Отправьте эту ссылку пользователю, которого хотите добавить:\n"
            f"{ip_link}",
            reply_markup=keyboard,
        )

    except httpx.HTTPError as e:
        await callback.message.answer(
            f"❌ Ошибка при создании приглашения: {e}"
        )
