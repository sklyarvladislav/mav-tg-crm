from .create import router as make_document_router
from .delete import router as delete_document_router
from .get import router as get_document_router

__all__ = [
    "delete_document_router",
    "get_document_router",
    "make_document_router",
]
