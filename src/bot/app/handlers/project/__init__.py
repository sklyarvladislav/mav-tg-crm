from .back_to_project import router as back_to_project_router
from .create import router as make_project_router
from .my_projects import router as my_projects_router
from .project_info import router as project_info_router
from .project_settings import router as project_settings_router
from .projects import router as projects_router

__all__ = [
    "back_to_project_router",
    "make_project_router",
    "my_projects_router",
    "project_info_router",
    "project_settings_router",
    "projects_router",
]
