from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select

from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import ProjectParticipant


@dataclass(slots=True)
class DeleteParticipantGate(PostgresGate):
    async def __call__(self, user_id: int, project_id: UUID) -> bool:
        stmt_select = select(ProjectParticipant).where(
            ProjectParticipant.user_id == user_id,
            ProjectParticipant.project_id == project_id,
        )
        participant = (
            await self.session.execute(stmt_select)
        ).scalar_one_or_none()

        if participant is None:
            return False

        stmt_delete = delete(ProjectParticipant).where(
            ProjectParticipant.user_id == user_id,
            ProjectParticipant.project_id == project_id,
        )
        await self.session.execute(stmt_delete)
        await self.session.commit()

        return True
