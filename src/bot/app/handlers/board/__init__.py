from .create import router as make_board_router
from .delete import router as delete_board_router
from .get import router as get_board_router
from .kanban import router as kanban_board_router
from .open import router as open_board_router

__all__ = [
    "delete_board_router",
    "get_board_router",
    "kanban_board_router",
    "make_board_router",
    "open_board_router",
]
