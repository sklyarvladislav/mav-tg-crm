from dishka import Provider, Scope, provide_all

from src.api.usecases.document.delete_document import DeleteDocumentUsecase
from src.api.usecases.document.get_document import GetDocumentUsecase
from src.api.usecases.document.update_document import UpdateDocumentUsecase
from src.api.usecases.project.delete_project import DeleteProjectUsecase
from src.api.usecases.project.get_project import GetProjectUsecase
from src.api.usecases.project.update_project import UpdateProjectUsecase


class UsecaseProvider(Provider):
    _get_usecases = provide_all(
        GetProjectUsecase,
        DeleteProjectUsecase,
        GetDocumentUsecase,
        DeleteDocumentUsecase,
        UpdateDocumentUsecase,
        UpdateProjectUsecase,
        scope=Scope.REQUEST,
    )
