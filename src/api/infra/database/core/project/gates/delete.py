from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select

from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Project


@dataclass(slots=True)
class DeleteProjectGate(PostgresGate):
    async def __call__(self, project_id: UUID) -> bool:
        stmt_select = select(Project).where(Project.project_id == project_id)
        project = (
            await self.session.execute(stmt_select)
        ).scalar_one_or_none()

        if project is None:
            return False

        stmt_delete = delete(Project).where(Project.project_id == project_id)
        await self.session.execute(stmt_delete)
        await self.session.commit()
        return True
