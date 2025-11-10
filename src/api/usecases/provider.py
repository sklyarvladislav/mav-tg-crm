from dishka import Provider, Scope, provide_all

from src.api.usecases.board.delete_board import DeleteBoardUsecase
from src.api.usecases.board.get_board import GetBoardUsecase
from src.api.usecases.board.update_board import UpdateBoardUsecase
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
        UpdateProjectUsecase,
        GetDocumentUsecase,
        DeleteDocumentUsecase,
        UpdateDocumentUsecase,
        GetBoardUsecase,
        DeleteBoardUsecase,
        UpdateBoardUsecase,
        scope=Scope.REQUEST,
    )
