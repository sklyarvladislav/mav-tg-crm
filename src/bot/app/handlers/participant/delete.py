import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("lp_"))
async def lp_confirm(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("lp_", "")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚪 Да, выйти",
                    callback_data=f"clp_{project_id}",  # <--- ИЗМЕНЕНО
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Нет, остаться",
                    callback_data=f"get_participant_{project_id}",
                )
            ],
        ]
    )

    await callback.message.edit_text(
        "❓ Вы уверены, что хотите покинуть этот проект?",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("clp_"))  # <--- ИЗМЕНЕНО
async def lp_execute(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("clp_", "")  # <--- ИЗМЕНЕНО
    user_id = callback.from_user.id

    await execute_delete(callback, project_id, user_id, is_self_leave=True)


@router.callback_query(F.data.startswith("kp_"))
async def kp_confirm(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")
    project_id = parts[1]
    target_user_id = parts[2]

    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            f"http://mav_web:80/user/{target_user_id}"
        )
        username = user_resp.json().get("username", "Unknown")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Да, исключить",
                    callback_data=f"ckp_{project_id}_{target_user_id}",  # <--- ИЗМЕНЕНО
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Отмена",
                    callback_data=f"mp_{project_id}_{target_user_id}",  # <--- СОКРАЩЕНО
                )
            ],
        ]
    )

    await callback.message.edit_text(
        f"❓ Вы уверены, что хотите исключить <b>{username}</b> из проекта?",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("ckp_"))  # <--- ИЗМЕНЕНО
async def kp_execute(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")
    project_id = parts[1]
    target_user_id = parts[2]
    await execute_delete(
        callback, project_id, target_user_id, is_self_leave=False
    )


async def execute_delete(
    callback: CallbackQuery,
    project_id: str,
    target_user_id: int | str,
    is_self_leave: bool,
) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"http://mav_web:80/participant/{project_id}/{target_user_id}"
        )

        if response.status_code == status.HTTP_200_OK:
            if is_self_leave:
                msg = "✅ Вы успешно вышли из проекта"
                back_btn = InlineKeyboardButton(
                    text="⬅️ К списку проектов",
                    callback_data="back_to_projects",
                )
            else:
                msg = "✅ Участник исключен"
                back_btn = InlineKeyboardButton(
                    text="⬅️ К списку участников",
                    callback_data=f"get_participant_{project_id}",
                )

            keyboard = InlineKeyboardMarkup(inline_keyboard=[[back_btn]])
            await callback.message.edit_text(msg, reply_markup=keyboard)
        else:
            await callback.answer(
                "❌ Ошибка выполнения операции", show_alert=True
            )
