from dataclasses import asdict, dataclass
from uuid import UUID

from src.api.application.schemas.project import (
    ProjectSchema,
    ProjectUpdateSchema,
)
from src.api.infra.database.core.project.gates.update import UpdateProjectGate


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateProjectUsecase:
    update_project: UpdateProjectGate

    async def __call__(
        self, project_id: UUID, data: ProjectUpdateSchema
    ) -> ProjectSchema:
        update_data = {k: v for k, v in asdict(data).items() if v is not None}
        return await self.update_project(
            project_id=project_id, data=update_data
        )
