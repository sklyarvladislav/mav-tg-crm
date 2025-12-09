from io import BytesIO

import httpx
from aiogram import F, Router
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status
from PIL import Image, ImageDraw, ImageFont

router = Router()


def generate_kanban_image(
    board_name: str, columns: list, tasks: list
) -> BytesIO:
    """Generate a Kanban board visualization as an image."""

    # Constants for layout
    column_width = 300
    column_padding = 20
    header_height = 80
    task_height = 100
    task_padding = 10
    footer_height = 50
    max_tasks_per_column = 10
    max_task_name_length = 30

    # Colors
    bg_color = (248, 249, 250)
    column_bg = (255, 255, 255)
    column_border = (222, 226, 230)
    header_bg = (52, 58, 64)
    header_text = (255, 255, 255)
    text_color = (33, 37, 41)
    task_bg = (233, 236, 239)

    # Calculate dimensions
    num_columns = max(len(columns), 1)
    width = (column_width + column_padding) * num_columns + column_padding

    # Group tasks by column
    tasks_by_column = {}
    for task in tasks:
        column_id = task.get("column_id")
        if column_id:
            if column_id not in tasks_by_column:
                tasks_by_column[column_id] = []
            tasks_by_column[column_id].append(task)

    # Calculate max tasks in any column
    max_tasks = max(
        [len(tasks_by_column.get(col["column_id"], [])) for col in columns]
        or [0]
    )
    height = (
        header_height
        + (task_height + task_padding) * max(max_tasks, 1)
        + footer_height
    )

    # Create image
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Load fonts - DejaVu fonts have excellent Unicode/Cyrillic support
    # These are installed via ttf-dejavu package in Alpine Linux
    try:
        title_font = ImageFont.truetype(
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 24
        )
        header_font = ImageFont.truetype(
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf", 18
        )
        task_font = ImageFont.truetype(
            "/usr/share/fonts/dejavu/DejaVuSans.ttf", 14
        )
    except (OSError, IOError):
        # Fallback to default font (limited Unicode support)
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        task_font = ImageFont.load_default()

    # Draw header with board name
    draw.rectangle([(0, 0), (width, header_height)], fill=header_bg)

    # Center the board name
    title_text = f"Kanban: {board_name}"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(
        ((width - title_width) // 2, 25),
        title_text,
        fill=header_text,
        font=title_font,
    )

    # Draw columns
    for i, column in enumerate(columns):
        x_offset = column_padding + i * (column_width + column_padding)
        y_offset = header_height + column_padding

        # Draw column background
        column_rect = [
            (x_offset, y_offset),
            (x_offset + column_width, height - footer_height),
        ]
        draw.rectangle(
            column_rect, fill=column_bg, outline=column_border, width=2
        )

        # Draw column header
        column_header_rect = [
            (x_offset + 5, y_offset + 5),
            (x_offset + column_width - 5, y_offset + 40),
        ]
        draw.rectangle(column_header_rect, fill=header_bg)

        # Column name
        column_name = column["name"]
        column_tasks = tasks_by_column.get(column["column_id"], [])
        header_text_str = f"{column_name} ({len(column_tasks)})"

        # Center text in column header
        header_bbox = draw.textbbox((0, 0), header_text_str, font=header_font)
        header_width = header_bbox[2] - header_bbox[0]
        text_x = x_offset + (column_width - header_width) // 2
        draw.text(
            (text_x, y_offset + 15),
            header_text_str,
            fill=header_text,
            font=header_font,
        )

        # Draw tasks in column
        task_y = y_offset + 50
        for task in column_tasks[:max_tasks_per_column]:
            task_rect = [
                (x_offset + 10, task_y),
                (x_offset + column_width - 10, task_y + task_height - 10),
            ]
            draw.rectangle(
                task_rect, fill=task_bg, outline=column_border, width=1
            )

            # Task name (truncate if too long)
            task_name = task["name"]
            if len(task_name) > max_task_name_length:
                task_name = task_name[:max_task_name_length] + "..."
            draw.text(
                (x_offset + 15, task_y + 10),
                task_name,
                fill=text_color,
                font=task_font,
            )

            # Task priority indicator
            priority_colors = {
                "HIGH": (220, 53, 69),
                "MEDIUM": (255, 193, 7),
                "LOW": (40, 167, 69),
                "FROZEN": (108, 117, 125),
            }
            priority = task.get("priority", "WITHOUT")
            if priority in priority_colors:
                priority_circle = [
                    (x_offset + 15, task_y + 35),
                    (x_offset + 25, task_y + 45),
                ]
                draw.ellipse(priority_circle, fill=priority_colors[priority])
                draw.text(
                    (x_offset + 30, task_y + 32),
                    priority,
                    fill=text_color,
                    font=task_font,
                )

            task_y += task_height

        # If there are more tasks, show indicator
        if len(column_tasks) > max_tasks_per_column:
            draw.text(
                (x_offset + 15, task_y + 5),
                f"+ {len(column_tasks) - max_tasks_per_column} more...",
                fill=text_color,
                font=task_font,
            )

    # Save to BytesIO
    output = BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return output


@router.callback_query(F.data.startswith("kanban_"))
async def show_kanban(callback: CallbackQuery) -> None:
    await callback.answer()
    board_id = callback.data.replace("kanban_", "")

    async with httpx.AsyncClient() as client:
        # Get board info
        board_resp = await client.get(f"http://web:80/board/{board_id}")
        if board_resp.status_code != status.HTTP_200_OK:
            await callback.message.answer("❌ Не удалось получить доску")
            return
        board = board_resp.json()

        # Get columns
        columns_resp = await client.get(
            f"http://web:80/column/{board_id}/columns"
        )
        if columns_resp.status_code != status.HTTP_200_OK:
            await callback.message.answer("❌ Не удалось получить колонки")
            return
        columns = columns_resp.json()

        # Get tasks
        tasks_resp = await client.get(
            f"http://web:80/task/{board['project_id']}/tasks"
        )
        tasks = (
            tasks_resp.json()
            if tasks_resp.status_code == status.HTTP_200_OK
            else []
        )

        # Filter tasks for this board
        board_tasks = [
            task for task in tasks if task.get("board_id") == board_id
        ]

    if not columns:
        await callback.message.answer(
            "❌ На доске нет колонок для визуализации"
        )
        return

    # Generate kanban image
    try:
        image_bytes = generate_kanban_image(
            board["name"], columns, board_tasks
        )

        # Send photo
        photo = BufferedInputFile(
            image_bytes.read(), filename=f"kanban_{board_id}.png"
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад к доске",
                        callback_data=f"open_board_{board_id}",
                    )
                ]
            ]
        )

        await callback.message.answer_photo(
            photo=photo,
            caption=f"🖼️ Kanban доски: {board['name']}\n"
            f"Колонок: {len(columns)}\n"
            f"Задач: {len(board_tasks)}",
            reply_markup=keyboard,
        )
    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка создания визуализации: {e!s}"
        )
