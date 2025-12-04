from src.api.application.enums.base import BaseENUM


class StatusTask(BaseENUM):
    DONE = "DONE"
    NOT_DONE = "NOT_DONE"


class PriorityTask(BaseENUM):
    WITHOUT = "WITHOUT"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    FROZEN = "FROZEN"
