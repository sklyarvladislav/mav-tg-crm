import contextlib

import httpx
from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from app.handlers.project.info import get_user_role
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("mp_"))
async def mp_menu(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")
    project_id = parts[1]
    target_user_id = parts[2]

    viewer_role = await get_user_role(project_id, callback.from_user.id)

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"http://mav_web:80/participant/{project_id}/user/{target_user_id}/role"
        )
        if resp.status_code != status.HTTP_200_OK:
            await callback.answer("Участник не найден")
            return
        target_role = resp.json()["role"]

        user_resp = await client.get(
            f"http://mav_web:80/user/{target_user_id}"
        )
        target_username = user_resp.json().get("username", "Unknown")

    keyboard = []

    if viewer_role == "OWNER" and target_role != "OWNER":
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="👑 Назначить Владельцем",
                    callback_data=f"sr_{project_id}_{target_user_id}_OWNER",
                )
            ]
        )

    if target_role != "OWNER" and (
        viewer_role == "OWNER"
        or (viewer_role == "ADMIN" and target_role == "USER")
    ):
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="⭐️ Назначить Админом",
                    callback_data=f"sr_{project_id}_{target_user_id}_ADMIN",
                )
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="👤 Назначить Юзером",
                    callback_data=f"sr_{project_id}_{target_user_id}_USER",
                )
            ]
        )

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="❌ Исключить",
                    callback_data=f"kp_{project_id}_{target_user_id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"get_participant_{project_id}"
            )
        ]
    )

    role_emoji = {"OWNER": "👑", "ADMIN": "⭐️", "USER": "👤"}
    emoji = role_emoji.get(target_role, "")

    with contextlib.suppress(TelegramBadRequest):
        await callback.message.edit_text(
            f"👤 Управление участником: <b>{target_username}</b>\n"
            f"Текущая роль: {emoji} {target_role}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        )


@router.callback_query(F.data.startswith("sr_"))
async def sr_check(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")
    project_id = parts[1]
    target_user_id = parts[2]
    new_role = parts[3]

    if new_role == "OWNER":
        async with httpx.AsyncClient() as client:
            user_resp = await client.get(
                f"http://mav_web:80/user/{target_user_id}"
            )
            target_username = user_resp.json().get("username", "Unknown")

        confirm_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Да, передать проект",
                        callback_data=f"co_{project_id}_{target_user_id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="❌ Отмена",
                        callback_data=f"mp_{project_id}_{target_user_id}",
                    )
                ],
            ]
        )

        await callback.message.edit_text(
            f"❓ Вы уверены, что хотите передать проект пользователю <b>{target_username}</b>?\n\n"
            f"⚠️ Вы потеряете статус Владельца и станете Администратором.",
            reply_markup=confirm_kb,
        )
    else:
        await execute_role_change(
            callback, project_id, target_user_id, new_role
        )


@router.callback_query(F.data.startswith("co_"))
async def co_transfer(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")
    project_id = parts[1]
    target_user_id = parts[2]

    self_user_id = callback.from_user.id

    async with httpx.AsyncClient() as client:
        resp_promote = await client.patch(
            f"http://mav_web:80/participant/{target_user_id}",
            params={"project_id": project_id},
            json={"role": "OWNER"},
        )

        if resp_promote.status_code != status.HTTP_200_OK:
            await callback.answer(
                "❌ Ошибка назначения нового владельца", show_alert=True
            )
            return

        resp_demote = await client.patch(
            f"http://mav_web:80/participant/{self_user_id}",
            params={"project_id": project_id},
            json={"role": "USER"},
        )

        if resp_demote.status_code == status.HTTP_200_OK:
            await callback.answer("✅ Права переданы")

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⬅️ К списку участников",
                            callback_data=f"get_participant_{project_id}",
                        )
                    ]
                ]
            )

            await callback.message.edit_text(
                "👑 <b>Права Владельца успешно переданы.</b>\n\n"
                "Вы стали обычным участником проекта.",
                reply_markup=keyboard,
            )
        else:
            await callback.answer(
                "⚠️ Новый владелец назначен, но понизить вас не удалось",
                show_alert=True,
            )


async def execute_role_change(
    callback: CallbackQuery,
    project_id: str,
    target_user_id: str,
    new_role: str,
) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"http://mav_web:80/participant/{target_user_id}",
            params={"project_id": project_id},
            json={"role": new_role},
        )

        if response.status_code == status.HTTP_200_OK:
            await callback.answer("✅ Роль изменена")
            new_callback = callback.model_copy(
                update={"data": f"mp_{project_id}_{target_user_id}"}
            )
            await mp_menu(new_callback)

            await mp_menu(callback)
        else:
            await callback.answer("❌ Ошибка смены роли", show_alert=True)
