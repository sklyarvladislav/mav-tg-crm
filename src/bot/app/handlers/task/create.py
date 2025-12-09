from datetime import UTC, datetime
from uuid import uuid4

import httpx
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
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


class MakeTask(StatesGroup):
    task_name = State()
    task_description = State()

    choose_document_mode = State()
    choose_existing_document = State()
    new_document_name = State()
    new_document_link = State()

    priority = State()
    deadline = State()
    executor = State()


@router.callback_query(F.data.startswith("create_task_col_"))
async def start_create_task_in_column(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await callback.answer()
    # Format: create_task_col_{column_id}
    column_id = callback.data.replace("create_task_col_", "")

    # Get column info to get board_id, then board info to get project_id
    async with httpx.AsyncClient() as client:
        column_response = await client.get(f"http://web:80/column/{column_id}")
        if column_response.status_code != status.HTTP_200_OK:
            await callback.message.answer(
                "❌ Не удалось получить информацию о колонке"
            )
            return
        column = column_response.json()
        board_id = column["board_id"]

        board_response = await client.get(f"http://web:80/board/{board_id}")
        if board_response.status_code != status.HTTP_200_OK:
            await callback.message.answer(
                "❌ Не удалось получить информацию о доске"
            )
            return
        board = board_response.json()
        project_id = board["project_id"]

    await state.update_data(
        project_id=project_id, board_id=board_id, column_id=column_id
    )
    await state.set_state(MakeTask.task_name)
    await callback.message.answer("Введите название задачи:")


@router.callback_query(F.data.startswith("create_task_"))
async def start_create_task(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await callback.answer()
    project_id = callback.data.replace("create_task_", "")
    await state.update_data(
        project_id=project_id, board_id=None, column_id=None
    )

    await state.set_state(MakeTask.task_name)
    await callback.message.answer("Введите название задачи:")


@router.message(MakeTask.task_name)
async def enter_task_name(message: Message, state: FSMContext) -> None:
    await state.update_data(task_name=message.text)

    await state.set_state(MakeTask.task_description)
    await message.answer("Введите описание задачи:")


@router.message(MakeTask.task_description)
async def enter_task_description(message: Message, state: FSMContext) -> None:
    await state.update_data(task_description=message.text)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📄 Выбрать существующий документ",
                    callback_data="doc_choose_existing",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🆕 Создать новый документ",
                    callback_data="doc_create_new",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚫 Без документа", callback_data="doc_none"
                )
            ],
        ]
    )

    await state.set_state(MakeTask.choose_document_mode)
    await message.answer(
        "Выберите способ добавить документ:", reply_markup=keyboard
    )


@router.callback_query(
    MakeTask.choose_document_mode, F.data == "doc_choose_existing"
)
async def choose_existing_document(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await callback.answer()
    data = await state.get_data()
    project_id = data["project_id"]

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"http://web:80/document/{project_id}/documents"
        )

    docs = resp.json() if resp.status_code == status.HTTP_200_OK else []

    if not docs:
        await callback.message.answer(
            "В проекте нет документов. Создайте новый."
        )
        await state.set_state(MakeTask.new_document_name)
        await callback.message.answer("Введите название документа:")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=doc["name"],
                    callback_data=f"doc_select_{doc['document_id']}",
                )
            ]
            for doc in docs
        ]
    )

    await state.set_state(MakeTask.choose_existing_document)
    await callback.message.answer("Выберите документ:", reply_markup=keyboard)


@router.callback_query(
    MakeTask.choose_existing_document, F.data.startswith("doc_select_")
)
async def select_existing_document(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await callback.answer()
    document_id = callback.data.replace("doc_select_", "")
    await state.update_data(document_id=document_id)
    await start_priority_select(callback.message, state)


@router.callback_query(
    MakeTask.choose_document_mode, F.data == "doc_create_new"
)
async def doc_create_new(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(MakeTask.new_document_name)
    await callback.message.answer("Введите название документа:")


@router.message(MakeTask.new_document_name)
async def doc_enter_name(message: Message, state: FSMContext) -> None:
    await state.update_data(new_doc_name=message.text)
    await state.set_state(MakeTask.new_document_link)
    await message.answer("Введите ссылку на документ:")


@router.message(MakeTask.new_document_link)
async def doc_create(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://web:80/document",
            json={
                "name": data["new_doc_name"],
                "link": message.text,
                "project_id": data["project_id"],
            },
        )

    if resp.status_code != status.HTTP_200_OK:
        await message.answer("❌ Ошибка создания документа. Попробуйте снова.")
        return

    doc = resp.json()
    await state.update_data(document_id=doc["document_id"])

    await message.answer(f"📄 Документ создан: {doc['name']}")
    await start_priority_select(message, state)


@router.callback_query(MakeTask.choose_document_mode, F.data == "doc_none")
async def no_document(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(document_id=None)
    await start_priority_select(callback.message, state)


async def start_priority_select(message: Message, state: FSMContext) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚪ Без приоритета", callback_data="priority_WITHOUT"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🟢 Низкий", callback_data="priority_LOW"
                ),
                InlineKeyboardButton(
                    text="🟡 Средний", callback_data="priority_MEDIUM"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔴 Высокий", callback_data="priority_HIGH"
                ),
                InlineKeyboardButton(
                    text="🧊 Заморожен", callback_data="priority_FROZEN"
                ),
            ],
        ]
    )

    await state.set_state(MakeTask.priority)
    await message.answer("Выберите приоритет задачи:", reply_markup=keyboard)


@router.callback_query(MakeTask.priority, F.data.startswith("priority_"))
async def choose_priority(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(priority=callback.data.replace("priority_", ""))

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚫 Нет (без дедлайна)", callback_data="deadline_none"
                )
            ]
        ]
    )

    await state.set_state(MakeTask.deadline)
    await callback.message.answer(
        "Введите дедлайн (ДД-ММ или ДД-ММ-ГГГГ) или нажмите кнопку ниже:",
        reply_markup=keyboard,
    )


@router.callback_query(MakeTask.deadline, F.data == "deadline_none")
async def skip_deadline(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(deadline=None)
    await start_executor_select(callback.message, state)


@router.message(MakeTask.deadline)
async def enter_deadline(message: Message, state: FSMContext) -> None:
    deadline_text = message.text.lower()
    deadline_value = None
    full_date_parts = 3

    if deadline_text != "нет":
        try:
            current_date = datetime.now(UTC)
            current_year = current_date.year

            # Try DD-MM-YYYY format first
            parts = message.text.split("-")
            if len(parts) == full_date_parts:
                deadline_value = (
                    datetime.strptime(message.text, "%d-%m-%Y")
                    .replace(tzinfo=UTC)
                    .isoformat()
                )
            # Try DD-MM format
            else:
                day, month = map(int, parts)
                year = current_year

                # If the date is in the past (earlier than current month/day), assume next year
                if month < current_date.month or (
                    month == current_date.month and day < current_date.day
                ):
                    year = current_year + 1

                deadline_value = datetime(
                    year, month, day, tzinfo=UTC
                ).isoformat()
        except (ValueError, AttributeError):
            await message.answer(
                "❌ Неверный формат. Примеры: 25-12, 31-01-2025"
            )
            return

    await state.update_data(deadline=deadline_value)
    await start_executor_select(message, state)


async def start_executor_select(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    project_id = data["project_id"]

    keyboard_buttons = []

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"http://web:80/participant/{project_id}/participants"
        )

        if resp.status_code == status.HTTP_200_OK:
            participants = resp.json()

            for p in participants:
                user_id = p["user_id"]
                role = p["role"]

                user_resp = await client.get(f"http://web:80/user/{user_id}")
                if user_resp.status_code == status.HTTP_200_OK:
                    user_data = user_resp.json()
                    name = (
                        user_data.get("username")
                        or user_data.get("short_name")
                        or f"ID {user_id}"
                    )
                else:
                    name = f"ID {user_id}"

                keyboard_buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{name} ({role})",
                            callback_data=f"user_{user_id}",
                        )
                    ]
                )
        else:
            await message.answer("⚠️ Не удалось загрузить участников проекта.")

    keyboard_buttons.append(
        [
            InlineKeyboardButton(
                text="🚫 Без исполнителя", callback_data="user_none"
            )
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await state.set_state(MakeTask.executor)
    await message.answer("Выберите исполнителя:", reply_markup=keyboard)


@router.callback_query(MakeTask.executor, F.data.startswith("user_"))
async def choose_executor(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    executor_raw = callback.data.replace("user_", "")
    executor_id = None if executor_raw == "none" else int(executor_raw)

    await state.update_data(executor_id=executor_id)
    data = await state.get_data()

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"http://web:80/task/{data['project_id']}/tasks"
        )
        tasks = resp.json() if resp.status_code == status.HTTP_200_OK else []
        number = len(tasks) + 1

        # Get column info if column_id is provided to derive status
        task_status = "NOT_DONE"
        if data.get("column_id"):
            column_resp = await client.get(
                f"http://web:80/column/{data['column_id']}"
            )
            if column_resp.status_code == status.HTTP_200_OK:
                column = column_resp.json()
                # Use column name as status
                task_status = column["name"]

        payload = {
            "task_id": str(uuid4()),
            "name": data.get("task_name") or "Без названия",
            "text": data.get("task_description") or "",
            "document_id": data.get("document_id"),
            "user_id": executor_id,
            "project_id": data["project_id"],
            "board_id": data.get("board_id"),
            "column_id": data.get("column_id"),
            "number": number,
            "priority": data.get("priority") or "WITHOUT",
            "deadline": data.get("deadline"),
            "status": task_status,
        }

        resp = await client.post("http://web:80/task", json=payload)

    if resp.status_code != status.HTTP_200_OK:
        await callback.message.answer("❌ Ошибка при создании задачи")
        await state.clear()
        return

    task = resp.json()

    # Send notification to executor if assigned
    if executor_id:
        try:
            from bot.bot import bot  # noqa: PLC0415

            await bot.send_message(
                executor_id,
                f"📋 Вам назначена новая задача!\n\n"
                f"Название: {task['name']}\n"
                f"Описание: {task['text']}\n"
                f"Приоритет: {task['priority']}\n"
                f"Дедлайн: {task.get('deadline') or 'Не указан'}",
            )
        except Exception as e:
            logger.error(f"Failed to send notification to executor: {e}")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"get_tasks_{data['project_id']}",
                )
            ]
        ]
    )

    await callback.message.answer(
        f"✅ Задача создана!\n\n"
        f"Название: {task['name']}\n"
        f"Номер: {task.get('number', '-')}\n"
        f"Приоритет: {task['priority']}\n"
        f"Статус: {task['status']}",
        reply_markup=keyboard,
    )

    await state.clear()
