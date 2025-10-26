from src.api.application.enums.base import BaseENUM


class StatusProject(BaseENUM):
    IN_PROGRESS = "In progress"
    FINISHED = "Finished"
    STOPPED = "Stopped"
    PLANNED = "Planned"
