from dataclasses import dataclass
from uuid import UUID

from src.api.infra.database.core.project.gates.delete_participant import (
    DeleteParticipantGate,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class DeleteParticipantUsecase:
    delete_participant: DeleteParticipantGate

    async def __call__(self, user_id: int, project_id: UUID) -> bool:
        return await self.delete_participant(
            user_id=user_id, project_id=project_id
        )
