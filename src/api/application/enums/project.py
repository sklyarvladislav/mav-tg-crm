from src.api.application.enums.base import BaseENUM


class StatusProject(BaseENUM):
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
    STOPPED = "STOPPED"
    PLANNED = "PLANNED"
