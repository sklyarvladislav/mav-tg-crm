from dataclasses import dataclass
from uuid import UUID

from src.api.infra.database.core.project.gates.delete import DeleteProjectGate


@dataclass(slots=True, frozen=True, kw_only=True)
class ChangeRoleParticipantUsecase:
    delete_project: DeleteProjectGate

    async def __call__(self, project_id: UUID) -> bool:
        return await self.delete_project(project_id=project_id)
