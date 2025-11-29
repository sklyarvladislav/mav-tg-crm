import httpx
from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from fastapi import status

router = Router()


@router.callback_query(F.data.startswith("delete_board_"))
async def delete_board(callback: CallbackQuery) -> None:
    board_id = callback.data.replace("delete_board_", "")

    async with httpx.AsyncClient() as client:
        board_response = await client.get(f"http://web:80/board/{board_id}")
        if board_response.status_code != status.HTTP_200_OK:
            await callback.message.edit_text("❌ Ошибка получения доски")
            return

        board = board_response.json()
        project_id = board["project_id"]
        deleted_position = board["position"]

        delete_response = await client.delete(
            f"http://web:80/board/{board_id}"
        )
        if delete_response.status_code != status.HTTP_200_OK:
            await callback.message.edit_text("❌ Ошибка удаления доски")
            return

        boards_response = await client.get(
            f"http://web:80/board/{project_id}/boards"
        )
        if boards_response.status_code == status.HTTP_200_OK:
            boards = boards_response.json()
            for b in boards:
                if b["position"] > deleted_position:
                    await client.patch(
                        f"http://web:80/board/{b['board_id']}",
                        json={"position": b["position"] - 1},
                    )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ Назад",
                        callback_data=f"get_board_{project_id}",
                    )
                ]
            ]
        )
        await callback.message.edit_text(
            "✅ Доска удалена", reply_markup=keyboard
        )
