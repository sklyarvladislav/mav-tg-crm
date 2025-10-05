from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class Usecase(Protocol):
    async def __call__(self, *args: object, **kwargs: object) -> None:
        raise NotImplementedError()
