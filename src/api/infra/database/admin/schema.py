from dataclasses import fields

from adaptix import Retort

from src.api.infra.database.errors import UpdateError

retort = Retort()


def update_schema(schema: type) -> type:
    def __check_if_any_none(self: "schema") -> None:
        if all(getattr(self, field.name) is None for field in fields(self)):
            raise UpdateError(
                error="Хотя бы одно поле должен быть заполненным",
                model_name=self.__class__.__name__,
            )

    schema.__post_init__ = __check_if_any_none
    return schema
