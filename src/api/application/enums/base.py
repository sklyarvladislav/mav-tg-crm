from enum import Enum
from typing import Any, Self


class BaseENUM(Enum):
    def __contains__(self, item: str) -> bool:
        return item in self.values()

    @classmethod
    def _missing_(cls, value: object) -> Self | None:
        for member in cls:
            if (
                isinstance(value, str)
                and member.value.upper() == value.upper()
            ):
                return member

        return None

    @classmethod
    def keys(cls) -> list[str]:
        """Returns a list of all the enum keys."""
        return cls._member_names_

    @classmethod
    def values(cls) -> list[str]:
        """Returns a list of all the enum values."""
        return list(cls._value2member_map_.keys())

    @classmethod
    def to_dict(cls) -> dict[str, dict[str, Any]]:
        """Return enum as dict."""
        return {cls.__name__: {member.name: member.value for member in cls}}
