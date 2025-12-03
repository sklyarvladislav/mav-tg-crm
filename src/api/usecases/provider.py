from dishka import Provider, Scope, provide_all

from src.api.usecases.board.delete_board import DeleteBoardUsecase
from src.api.usecases.board.get_board import GetBoardUsecase
from src.api.usecases.board.update_board import UpdateBoardUsecase
from src.api.usecases.column.delete_column import DeleteBoardColumnUsecase
from src.api.usecases.column.get_column import GetBoardColumnUsecase
from src.api.usecases.column.update_column import UpdateBoardColumnUsecase
from src.api.usecases.document.delete_document import DeleteDocumentUsecase
from src.api.usecases.document.get_document import GetDocumentUsecase
from src.api.usecases.document.update_document import UpdateDocumentUsecase
from src.api.usecases.participant.delete import DeleteParticipantUsecase
from src.api.usecases.project.delete_project import DeleteProjectUsecase
from src.api.usecases.project.get_project import GetProjectUsecase
from src.api.usecases.project.update_project import UpdateProjectUsecase
from src.api.usecases.task.delete_task import DeleteTaskUsecase
from src.api.usecases.task.get_task import GetTaskUsecase
from src.api.usecases.task.update_task import UpdateTaskUsecase


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
        GetBoardColumnUsecase,
        DeleteBoardColumnUsecase,
        UpdateBoardColumnUsecase,
        GetTaskUsecase,
        DeleteTaskUsecase,
        UpdateTaskUsecase,
        DeleteParticipantUsecase,
        scope=Scope.REQUEST,
    )
