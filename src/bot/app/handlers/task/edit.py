import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status
from structlog import get_logger

router = Router()
logger = get_logger()


@router.callback_query(F.data.startswith("edit_task_status_"))
async def choose_status_menu(callback: CallbackQuery) -> None:
    task_id = callback.data.replace("edit_task_status_", "")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="В работе",
                    callback_data=f"set_task_st_{task_id}_IN_PROGRESS",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Выполнена",
                    callback_data=f"set_task_st_{task_id}_DONE",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Не выполнена",
                    callback_data=f"set_task_st_{task_id}_NOT_DONE",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Отмена", callback_data=f"task_{task_id}"
                )
            ],
        ]
    )
    await callback.message.edit_text(
        "Выберите новый статус задачи:", reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("set_task_st_"))
async def set_task_status(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")

    task_id = parts[3]
    new_status = "_".join(parts[4:])

    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"http://web:80/task/{task_id}", json={"status": new_status}
        )

    if resp.status_code == status.HTTP_200_OK:
        await callback.answer("✅ Статус обновлен")

        await callback.message.edit_text(
            "✅ Статус успешно изменен!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔙 К задаче", callback_data=f"task_{task_id}"
                        )
                    ]
                ]
            ),
        )
    else:
        await callback.answer("❌ Ошибка обновления", show_alert=True)


@router.callback_query(F.data.startswith("edit_task_executor_"))
async def choose_executor_menu(callback: CallbackQuery) -> None:
    task_id = callback.data.replace("edit_task_executor_", "")

    async with httpx.AsyncClient() as client:
        task_resp = await client.get(f"http://web:80/task/{task_id}")
        if task_resp.status_code != status.HTTP_200_OK:
            await callback.answer("Ошибка доступа к задаче")
            return
        project_id = task_resp.json()["project_id"]

        part_resp = await client.get(
            f"http://web:80/participant/{project_id}/participants"
        )
        participants = (
            part_resp.json()
            if part_resp.status_code == status.HTTP_200_OK
            else []
        )

    buttons = []
    async with httpx.AsyncClient() as client:
        for p in participants:
            user_id = p["user_id"]
            user_resp = await client.get(f"http://web:80/user/{user_id}")
            if user_resp.status_code == status.HTTP_200_OK:
                u = user_resp.json()
                name = u.get("short_name") or u.get("username")
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{name} ({p['role']})",
                            callback_data=f"set_task_exec_{task_id}_{user_id}",
                        )
                    ]
                )

    buttons.append(
        [
            InlineKeyboardButton(
                text="🚫 Снять исполнителя",
                callback_data=f"set_task_exec_{task_id}_none",
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Отмена", callback_data=f"task_{task_id}"
            )
        ]
    )

    await callback.message.edit_text(
        "Выберите нового исполнителя:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("set_task_exec_"))
async def set_task_executor(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")
    task_id = parts[3]
    user_id_str = parts[4]

    new_executor_id = int(user_id_str) if user_id_str != "none" else None

    # Get task info before updating
    async with httpx.AsyncClient() as client:
        task_resp = await client.get(f"http://web:80/task/{task_id}")
        if task_resp.status_code != status.HTTP_200_OK:
            await callback.answer("❌ Ошибка", show_alert=True)
            return
        task = task_resp.json()

        resp = await client.patch(
            f"http://web:80/task/{task_id}", json={"user_id": new_executor_id}
        )

    if resp.status_code == status.HTTP_200_OK:
        # Send notification to new executor if assigned and not self-assigning
        assigner_id = callback.from_user.id
        if new_executor_id and new_executor_id != assigner_id:
            try:
                from bot.bot import bot  # noqa: PLC0415

                await bot.send_message(
                    new_executor_id,
                    f"📋 Вам назначена задача!\n\n"
                    f"Название: {task['name']}\n"
                    f"Описание: {task['text']}\n"
                    f"Приоритет: {task['priority']}\n"
                    f"Дедлайн: {task.get('deadline') or 'Без дедлайна'}",
                )
            except Exception as e:
                logger.error(f"Failed to send notification to executor: {e}")

        await callback.answer("✅ Исполнитель изменен")
        await callback.message.edit_text(
            "✅ Исполнитель успешно обновлен!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔙 К задаче", callback_data=f"task_{task_id}"
                        )
                    ]
                ]
            ),
        )
    else:
        await callback.answer("❌ Ошибка", show_alert=True)
