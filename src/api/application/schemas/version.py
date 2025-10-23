from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class FullVersionSchema:
    id: int
    version: str
    description: str

    created_at: datetime
