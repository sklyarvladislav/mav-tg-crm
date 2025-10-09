from fastapi import status
from src.api.application.errors import BaseError


class DatabaseError(BaseError):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        super().__init__(message=message, status_code=status_code)


class NotFoundError(DatabaseError):
    def __init__(self, model_name: str) -> None:
        super().__init__(
            message=f"Модель {model_name} не найдена",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UniqueError(DatabaseError):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, model_name: str) -> None:
        super().__init__(
            f"Модель {model_name} содержит неуникальные значения",
            status_code=status.HTTP_409_CONFLICT,
        )


class CreateError(DatabaseError):
    def __init__(self, model_name: str, error: str | None) -> None:
        super().__init__(
            f"Модель {model_name} не может быть создана {error}",
            status_code=status.HTTP_409_CONFLICT,
        )


class UpdateError(DatabaseError):
    def __init__(self, model_name: str, error: str | None) -> None:
        super().__init__(
            f"Модель {model_name} не может быть обновлена {error}",
            status_code=status.HTTP_409_CONFLICT,
        )


class CursorPaginationError(BaseError):
    def __init__(self) -> None:
        super().__init__(
            message="Передан некорректный курсор",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
