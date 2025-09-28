from dishka import Provider, Scope, from_context

from src.core.config import Config


class DishkaProvider(Provider):
    _get_config = from_context(provides=Config, scope=Scope.APP)
