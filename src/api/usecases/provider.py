from dishka import Provider, Scope, provide_all

from src.api.usecases.board import (
    DeleteBoardUsecase,
    GetBoardUsecase,
    UpdateBoardUsecase,
)
from src.api.usecases.column import (
    DeleteBoardColumnUsecase,
    GetBoardColumnUsecase,
    UpdateBoardColumnUsecase,
)
from src.api.usecases.document import (
    DeleteDocumentUsecase,
    GetDocumentUsecase,
    UpdateDocumentUsecase,
)
from src.api.usecases.participant import (
    ChangeRoleParticipantUsecase,
    DeleteParticipantUsecase,
    GetParticipantUsecase,
)
from src.api.usecases.project import (
    DeleteProjectUsecase,
    GetProjectUsecase,
    UpdateProjectUsecase,
)
from src.api.usecases.task import (
    DeleteTaskUsecase,
    GetTaskUsecase,
    UpdateTaskUsecase,
)


class UsecaseProvider(Provider):
    _get_usecases = provide_all(
        # Project
        GetProjectUsecase,
        DeleteProjectUsecase,
        UpdateProjectUsecase,
        # Document
        GetDocumentUsecase,
        DeleteDocumentUsecase,
        UpdateDocumentUsecase,
        # Board
        GetBoardUsecase,
        DeleteBoardUsecase,
        UpdateBoardUsecase,
        # Board Column
        GetBoardColumnUsecase,
        DeleteBoardColumnUsecase,
        UpdateBoardColumnUsecase,
        # Task
        GetTaskUsecase,
        DeleteTaskUsecase,
        UpdateTaskUsecase,
        # Participant
        DeleteParticipantUsecase,
        GetParticipantUsecase,
        ChangeRoleParticipantUsecase,
        scope=Scope.REQUEST,
    )
