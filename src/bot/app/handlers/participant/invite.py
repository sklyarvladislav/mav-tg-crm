import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
)

router = Router()


@router.callback_query(F.data.startswith("invite_"))
async def invite(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("invite_", "")

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
        invite_link = f"https://t.me/{bot_username}?start=join_{token}"

        await callback.message.answer(
            "Отправьте эту ссылку пользователю, которого хотите добавить:\n"
            f"{invite_link}"
        )

    except httpx.HTTPError as e:
        await callback.message.answer(
            f"❌ Ошибка при создании приглашения: {e}"
        )
