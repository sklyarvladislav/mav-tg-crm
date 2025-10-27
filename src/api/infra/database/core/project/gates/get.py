from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from structlog import get_logger

from src.api.application.schemas.project import ProjectSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Project

logger = get_logger()


@dataclass(slots=True)
class GetProjectGate(PostgresGate):
    async def __call__(self, project_id: UUID) -> ProjectSchema:
        stmt = select(
            Project.project_id,
            Project.name,
            Project.description,
            Project.status,
            Project.owner,
        ).where(Project.project_id == project_id)

        return self.retort.load(
            (await self.session.execute(stmt)).mappings().fetchone(),
            ProjectSchema,
        )
