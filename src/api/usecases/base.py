from dataclasses import dataclass 
from typing import Protocol 

@dataclass(slots=True)
class Usecase(Protocol):
    async def __call__(self, *args, **kwargs) -> None:
        raise NotImplementedError()

