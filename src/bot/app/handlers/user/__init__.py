from .profile import router as profile_router
from .regist import router as regist_router
from .settings import router as settings_router
from .unknownmes import router as unknownmes_router

__all__ = [
    "profile_router",
    "regist_router",
    "settings_router",
    "unknownmes_router",
]
