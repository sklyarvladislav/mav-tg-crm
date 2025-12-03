from dataclasses import dataclass

from sqlalchemy import select
from structlog import get_logger

from src.api.application.schemas.participant import ParticipantSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import ProjectParticipant

logger = get_logger()


@dataclass(slots=True)
class GetParticipantGate(PostgresGate):
    async def __call__(self, user_id: int) -> ParticipantSchema:
        stmt = select(
            ProjectParticipant.project_id,
            ProjectParticipant.user_id,
            ProjectParticipant.role,
        ).where(ProjectParticipant.user_id == user_id)

        return self.retort.load(
            (await self.session.execute(stmt)).mappings().fetchone(),
            ParticipantSchema,
        )
