from dataclasses import dataclass

from starlette import status


class BaseError(Exception):
    def __init__(
        self,
        message: str = "An unknown error occurred.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.status_code = status_code
        self.message = message

    def __str__(self) -> str:
        return self.message


class BaseErrorGroup(ExceptionGroup[BaseError]):
    def __init__(self, errors: list[BaseError], **_: object) -> None:
        super().__init__("Some errors occurred", errors)


class ForbiddenError(BaseError):
    def __init__(self, message: str = "У вас недостаточно прав") -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN)


@dataclass(slots=True)
class UnauthorizedError(BaseError):
    message: str = "У вас недостаточно прав для этого действия"
    status_code: int = status.HTTP_401_UNAUTHORIZED
