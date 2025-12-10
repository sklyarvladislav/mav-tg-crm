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


async def get_user_role(project_id: str, user_id: int) -> str:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"http://web:80/participant/{project_id}/user/{user_id}/role"
            )
            if response.status_code == status.HTTP_200_OK:
                return response.json()["role"]
        except Exception:
            pass
    return "USER"


@router.callback_query(F.data.startswith("open_task_"))
async def open_task(callback: CallbackQuery) -> None:
    await callback.answer()
    task_id = callback.data.replace("open_task_", "")
    user_id = callback.from_user.id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/task/{task_id}")

        if response.status_code != status.HTTP_200_OK:
            await callback.message.answer("❌ Не удалось получить задачу")
            return

        task = response.json()
        project_id = task["project_id"]

        current_role = await get_user_role(project_id, user_id)

        document_link = None
        if task.get("document_id"):
            doc_resp = await client.get(
                f"http://web:80/document/{task['document_id']}"
            )
            if doc_resp.status_code == status.HTTP_200_OK:
                document = doc_resp.json()
                document_link = document.get("link")

        executor_name = "Не назначен"
        if task.get("user_id"):
            user_resp = await client.get(
                f"http://web:80/user/{task['user_id']}"
            )
            if user_resp.status_code == status.HTTP_200_OK:
                user = user_resp.json()
                executor_name = (
                    user.get("username")
                    or user.get("short_name")
                    or "Неизвестен"
                )

        # Get column name if task has column_id
        column_name = None
        if task.get("column_id"):
            column_resp = await client.get(
                f"http://web:80/column/{task['column_id']}"
            )
            if column_resp.status_code == status.HTTP_200_OK:
                column = column_resp.json()
                column_name = column["name"]

    deadline = task["deadline"] or "Без дедлайна"

    # If task has column_id, use column name as status
    if column_name:
        status_of_task = f"📋 {column_name}"
    else:
        status_map = {
            "DONE": "✅ Выполнено",
            "NOT_DONE": "Не выполнено",
            "IN_PROGRESS": "В работе",
        }
        status_of_task = status_map.get(task["status"], task["status"])

    priority_map = {
        "WITHOUT": "⚪ Без приоритета",
        "LOW": "🟢 Низкий",
        "MEDIUM": "🟡 Средний",
        "HIGH": "🔴 Высокий",
        "FROZEN": "🧊 Заморожен",
    }
    priority_text = priority_map.get(task["priority"], task["priority"])

    buttons = []

    # Only show status change if task is not attached to a column
    if not task.get("column_id"):
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🔄 Изменить статус",
                    callback_data=f"ts_{task['task_id']}",
                )
            ]
        )
    else:
        # If task is attached to a board/column, allow changing column
        buttons.append(
            [
                InlineKeyboardButton(
                    text="📋 Изменить колонку",
                    callback_data=f"tc_{task['task_id']}",
                )
            ]
        )

    if current_role in ["OWNER", "ADMIN"]:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🔥 Изменить приоритет",
                    callback_data=f"tp_{task['task_id']}",
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="👤 Изменить исполнителя",
                    callback_data=f"te_{task['task_id']}",
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить задачу",
                    callback_data=f"delete_task_{task['task_id']}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"get_tasks_{task['project_id']}",
            )
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        "📝 Задача:\n\n"
        f"Название: {task['name']}\n"
        f"Описание: {task['text']}\n"
        f"Медиа: {document_link or 'Нет'}\n"
        f"Исполнитель: {executor_name}\n"
        f"Статус: {status_of_task}\n"
        f"Приоритет: {priority_text}\n"
        f"Дедлайн: {deadline}\n",
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("ts_"))
async def change_task_status_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    task_id = callback.data.replace("ts_", "")

    current_status = None
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://web:80/task/{task_id}")
        if resp.status_code == status.HTTP_200_OK:
            current_status = resp.json().get("status")

    statuses = [
        ("NOT_DONE", "Не выполнена"),
        ("IN_PROGRESS", "В работе"),
        ("DONE", "Выполнена"),
    ]

    buttons = []
    for code, label in statuses:
        prefix = "✅ " if code == current_status else ""
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{prefix}{label}",
                    callback_data=f"tsset_{task_id}_{code}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад к задаче",
                callback_data=f"open_task_{task_id}",
            )
        ]
    )

    await callback.message.edit_text(
        "Выберите новый статус задачи:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("tsset_"))
async def set_task_status(callback: CallbackQuery) -> None:
    data = callback.data.replace("tsset_", "")
    task_id, new_status = data.split("_", maxsplit=1)

    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"http://web:80/task/{task_id}", json={"status": new_status}
        )

    if resp.status_code != status.HTTP_200_OK:
        await callback.answer("❌ Ошибка обновления статуса", show_alert=True)
        return

    await callback.message.edit_text(
        "✅ Статус успешно обновлен!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Вернуться к задаче",
                        callback_data=f"open_task_{task_id}",
                    )
                ]
            ]
        ),
    )


@router.callback_query(F.data.startswith("tp_"))
async def change_task_priority_menu(callback: CallbackQuery) -> None:
    task_id = callback.data.replace("tp_", "")

    async with httpx.AsyncClient() as client:
        task_resp = await client.get(f"http://web:80/task/{task_id}")
        if task_resp.status_code != status.HTTP_200_OK:
            await callback.answer("❌ Ошибка получения задачи")
            return
        project_id = task_resp.json()["project_id"]

    role = await get_user_role(project_id, callback.from_user.id)
    if role not in ["OWNER", "ADMIN"]:
        await callback.answer(
            "⛔ Только админы могут менять приоритет!", show_alert=True
        )
        return

    await callback.answer()

    current_priority = None
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://web:80/task/{task_id}")
        if resp.status_code == status.HTTP_200_OK:
            current_priority = resp.json().get("priority")

    priorities = [
        ("WITHOUT", "⚪ Без приоритета"),
        ("LOW", "🟢 Низкий"),
        ("MEDIUM", "🟡 Средний"),
        ("HIGH", "🔴 Высокий"),
        ("FROZEN", "🧊 Заморожен"),
    ]

    buttons = []
    for code, label in priorities:
        prefix = "✅ " if code == current_priority else ""
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{prefix}{label}",
                    callback_data=f"tpset_{task_id}_{code}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад к задаче",
                callback_data=f"open_task_{task_id}",
            )
        ]
    )

    await callback.message.edit_text(
        "Выберите новый приоритет задачи:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("tpset_"))
async def set_task_priority(callback: CallbackQuery) -> None:
    data = callback.data.replace("tpset_", "")
    task_id, new_priority = data.split("_", maxsplit=1)

    async with httpx.AsyncClient() as client:
        task_resp = await client.get(f"http://web:80/task/{task_id}")
        if task_resp.status_code != status.HTTP_200_OK:
            return
        project_id = task_resp.json()["project_id"]

    role = await get_user_role(project_id, callback.from_user.id)
    if role not in ["OWNER", "ADMIN"]:
        await callback.answer("⛔ Недостаточно прав!", show_alert=True)
        return

    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"http://web:80/task/{task_id}", json={"priority": new_priority}
        )

    if resp.status_code != status.HTTP_200_OK:
        await callback.answer(
            "❌ Ошибка обновления приоритета", show_alert=True
        )
        return

    await callback.message.edit_text(
        "✅ Приоритет успешно обновлен!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Вернуться к задаче",
                        callback_data=f"open_task_{task_id}",
                    )
                ]
            ]
        ),
    )


@router.callback_query(F.data.startswith("te_"))
async def change_task_executor_menu(callback: CallbackQuery) -> None:
    task_id = callback.data.replace("te_", "")

    async with httpx.AsyncClient() as client:
        task_resp = await client.get(f"http://web:80/task/{task_id}")
        if task_resp.status_code != status.HTTP_200_OK:
            await callback.message.answer("❌ Ошибка получения задачи")
            return
        task = task_resp.json()
        project_id = task["project_id"]
        current_user_id = task.get("user_id")

        role = await get_user_role(project_id, callback.from_user.id)
        if role not in ["OWNER", "ADMIN"]:
            await callback.answer(
                "⛔ Только админы могут менять исполнителя!", show_alert=True
            )
            return

        part_resp = await client.get(
            f"http://web:80/participant/{project_id}/participants"
        )

    await callback.answer()

    if part_resp.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Не удалось получить участников")
        return

    participants = part_resp.json()
    buttons = []

    async with httpx.AsyncClient() as client:
        for p in participants:
            user_id = p["user_id"]
            user_resp = await client.get(f"http://web:80/user/{user_id}")
            if user_resp.status_code != status.HTTP_200_OK:
                continue
            user = user_resp.json()
            name = (
                user.get("username")
                or user.get("short_name")
                or f"ID {user_id}"
            )

            prefix = "✅ " if user_id == current_user_id else ""

            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{prefix}{name} ({p['role']})",
                        callback_data=f"teset_{task_id}_{user_id}",
                    )
                ]
            )

    buttons.append(
        [
            InlineKeyboardButton(
                text="🚫 Без исполнителя",
                callback_data=f"teset_{task_id}_none",
            )
        ]
    )
    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад к задаче",
                callback_data=f"open_task_{task_id}",
            )
        ]
    )

    await callback.message.edit_text(
        "Выберите нового исполнителя:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("teset_"))
async def set_task_executor(callback: CallbackQuery) -> None:
    data = callback.data.replace("teset_", "")
    task_id, user_raw = data.split("_", maxsplit=1)

    async with httpx.AsyncClient() as client:
        task_resp = await client.get(f"http://web:80/task/{task_id}")
        if task_resp.status_code != status.HTTP_200_OK:
            return
        task = task_resp.json()
        project_id = task["project_id"]

    role = await get_user_role(project_id, callback.from_user.id)
    if role not in ["OWNER", "ADMIN"]:
        await callback.answer("⛔ Недостаточно прав!", show_alert=True)
        return

    if user_raw == "none":
        payload = {"user_id": None}
        new_executor_id = None
    else:
        new_executor_id = int(user_raw)
        payload = {"user_id": new_executor_id}

    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"http://web:80/task/{task_id}", json=payload
        )

    if resp.status_code != status.HTTP_200_OK:
        await callback.answer(
            "❌ Ошибка изменения исполнителя", show_alert=True
        )
        return

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

    await callback.message.edit_text(
        "✅ Исполнитель успешно изменен!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Вернуться к задаче",
                        callback_data=f"open_task_{task_id}",
                    )
                ]
            ]
        ),
    )


@router.callback_query(F.data.startswith("tc_"))
async def change_task_column_menu(callback: CallbackQuery) -> None:
    task_id = callback.data.replace("tc_", "")

    async with httpx.AsyncClient() as client:
        task_resp = await client.get(f"http://web:80/task/{task_id}")
        if task_resp.status_code != status.HTTP_200_OK:
            await callback.message.answer("❌ Ошибка получения задачи")
            return
        task = task_resp.json()
        board_id = task.get("board_id")
        current_column_id = task.get("column_id")

        if not board_id:
            await callback.answer(
                "❌ Задача не привязана к доске", show_alert=True
            )
            return

        # Get columns for this board
        columns_resp = await client.get(
            f"http://web:80/column/{board_id}/columns"
        )
        if columns_resp.status_code != status.HTTP_200_OK:
            await callback.message.answer("❌ Не удалось получить колонки")
            return

    await callback.answer()

    columns = columns_resp.json()
    buttons = []

    for column in columns:
        prefix = "✅ " if column["column_id"] == current_column_id else ""
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{prefix}{column['name']}",
                    callback_data=f"tcset_{task_id}_{column['column_id']}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад к задаче",
                callback_data=f"open_task_{task_id}",
            )
        ]
    )

    await callback.message.edit_text(
        "Выберите новую колонку:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("tcset_"))
async def set_task_column(callback: CallbackQuery) -> None:
    data = callback.data.replace("tcset_", "")
    task_id, column_id = data.split("_", maxsplit=1)

    async with httpx.AsyncClient() as client:
        # Get column name to update status
        column_resp = await client.get(f"http://web:80/column/{column_id}")
        if column_resp.status_code != status.HTTP_200_OK:
            await callback.answer(
                "❌ Ошибка получения колонки", show_alert=True
            )
            return

        column = column_resp.json()
        new_status = column["name"]

        # Update task with new column and status
        resp = await client.patch(
            f"http://web:80/task/{task_id}",
            json={"column_id": column_id, "status": new_status},
        )

    if resp.status_code != status.HTTP_200_OK:
        await callback.answer("❌ Ошибка обновления колонки", show_alert=True)
        return

    await callback.message.edit_text(
        "✅ Колонка успешно изменена!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Вернуться к задаче",
                        callback_data=f"open_task_{task_id}",
                    )
                ]
            ]
        ),
    )
