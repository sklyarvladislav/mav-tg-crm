from dataclasses import dataclass

from src.api.application.schemas.participant import ParticipantSchema
from src.api.infra.database.core.project.gates.get_participant import (
    GetParticipantGate,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class GetParticipantUsecase:
    get_participant: GetParticipantGate

    async def __call__(self, user_id: int) -> ParticipantSchema:
        participant: ParticipantSchema = await self.get_participant(
            user_id=user_id
        )

        return ParticipantSchema(
            project_id=participant.project_id,
            user_id=participant.user_id,
            role=participant.role,
        )
