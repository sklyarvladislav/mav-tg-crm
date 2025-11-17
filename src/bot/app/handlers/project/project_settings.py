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

router = Router()


@router.callback_query(F.data.startswith("settings_"))
async def project_settings(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("settings_", "")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏️ Изменить название",
                    callback_data=f"edit_name_{project_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Изменить описание",
                    callback_data=f"edit_desc_{project_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔄 Изменить статус",
                    callback_data=f"change_status_{project_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑️ Удалить проект",
                    callback_data=f"delete_{project_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад", callback_data=f"project_{project_id}"
                )
            ],
        ]
    )

    await callback.message.edit_text(
        "⚙️ Настройки проекта:", reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("delete_"))
async def delete_confirm(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("delete_", "")

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить удаление",
                    callback_data=f"confirm_delete_{project_id}",
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "❓ Вы уверены?", reply_markup=confirm_keyboard
    )


@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_project(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("confirm_delete_", "")

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://web:80/project/{project_id}")

    if response.status_code == status.HTTP_200_OK:
        await callback.message.edit_text("✅ Проект удален")
    else:
        await callback.message.edit_text("❌ Ошибка")


class EditProject(StatesGroup):
    name = State()
    description = State()


@router.callback_query(F.data.startswith("edit_name_"))
async def edit_name_start(callback: CallbackQuery, state: FSMContext) -> None:
    project_id = callback.data.replace("edit_name_", "")
    await state.set_state(EditProject.name)
    await state.update_data(project_id=project_id)
    await callback.message.edit_text("Введите новое название проекта:")


@router.callback_query(F.data.startswith("edit_desc_"))
async def edit_desc_start(callback: CallbackQuery, state: FSMContext) -> None:
    project_id = callback.data.replace("edit_desc_", "")
    await state.set_state(EditProject.description)
    await state.update_data(project_id=project_id)
    await callback.message.edit_text("Введите новое описание проекта:")


@router.message(EditProject.name)
async def edit_name_finish(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"http://web:80/project/{data['project_id']}",
            json={"name": message.text},
        )
    if response.status_code == status.HTTP_200_OK:
        await message.answer(
            "✅ Название обновлено",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⬅️ К проекту",
                            callback_data=f"project_{data['project_id']}",
                        )
                    ]
                ]
            ),
        )
    await state.clear()


@router.message(EditProject.description)
async def edit_desc_finish(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"http://web:80/project/{data['project_id']}",
            json={"description": message.text},
        )
    if response.status_code == status.HTTP_200_OK:
        await message.answer(
            "✅ Описание обновлено",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⬅️ К проекту",
                            callback_data=f"project_{data['project_id']}",
                        )
                    ]
                ]
            ),
        )
    await state.clear()


@router.callback_query(F.data.startswith("change_status_"))
async def change_status_menu(callback: CallbackQuery) -> None:
    project_id = callback.data.replace("change_status_", "")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://web:80/project/{project_id}")

    if response.status_code == status.HTTP_200_OK:
        project = response.json()
        current_status = project["status"]

        status_list = ["В работе", "На паузе", "Выполнен", "Отменен"]

        keyboard_buttons = []
        for status_item in status_list:
            if status_item == current_status:
                keyboard_buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"✅ {status_item}",
                            callback_data=f"status_{project_id}_{status_item}",
                        )
                    ]
                )
            else:
                keyboard_buttons.append(
                    [
                        InlineKeyboardButton(
                            text=status_item,
                            callback_data=f"status_{project_id}_{status_item}",
                        )
                    ]
                )

        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к проекту",
                    callback_data=f"project_{project_id}",
                )
            ]
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await callback.message.edit_text(
            "🔄 Выберите статус проекта:", reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("status_"))
async def set_status(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")
    project_id = parts[1]
    selected_status = parts[2]

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"http://web:80/project/{project_id}",
            json={"status": selected_status},
        )

    if response.status_code == status.HTTP_200_OK:
        status_list = ["В работе", "На паузе", "Выполнен", "Отменен"]

        keyboard_buttons = []
        for status_item in status_list:
            if status_item == selected_status:
                keyboard_buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"✅ {status_item}",
                            callback_data=f"status_{project_id}_{status_item}",
                        )
                    ]
                )
            else:
                keyboard_buttons.append(
                    [
                        InlineKeyboardButton(
                            text=status_item,
                            callback_data=f"status_{project_id}_{status_item}",
                        )
                    ]
                )

        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к проекту",
                    callback_data=f"project_{project_id}",
                )
            ]
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        await callback.message.edit_text(
            "🔄 Выберите статус проекта:", reply_markup=keyboard
        )
    else:
        await callback.answer("❌ Ошибка изменения статуса")
