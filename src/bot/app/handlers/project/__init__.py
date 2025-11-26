from .create import router as make_project_router
from .delete import router as delete_project_router
from .get import router as get_project_router
from .info import router as info_project_router
from .settings import router as settings_project_router

__all__ = [
    "delete_project_router",
    "get_project_router",
    "info_project_router",
    "make_project_router",
    "settings_project_router",
]
