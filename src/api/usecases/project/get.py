from dataclasses import dataclass
from uuid import UUID

from src.api.application.schemas.project import ProjectSchema
from src.api.infra.database.core.project.gates.get import GetProjectGate


@dataclass(slots=True, frozen=True, kw_only=True)
class GetProjectUsecase:
    get_project: GetProjectGate

    async def __call__(self, project_id: UUID) -> ProjectSchema:
        project: ProjectSchema = await self.get_project(project_id=project_id)

        return ProjectSchema(
            project_id=project.project_id,
            name=project.name,
            description=project.description,
            status=project.status,
        )
