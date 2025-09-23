from dishka import Provider, Scope, provide_all


class UsecaseProvider(Provider):
    _get_usecases = provide_all(
        scope=Scope.REQUEST,
    )
