from dishka import Provider, Scope, provide_all

from src.api.usecases.project.delete_project import DeleteProjectUsecase
from src.api.usecases.project.get_project import GetProjectUsecase


class UsecaseProvider(Provider):
    _get_usecases = provide_all(
        GetProjectUsecase,
        DeleteProjectUsecase,
        scope=Scope.REQUEST,
    )
