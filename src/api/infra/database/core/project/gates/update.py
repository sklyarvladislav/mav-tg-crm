from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import update
from structlog import get_logger

from src.api.application.schemas.project import ProjectSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Project

logger = get_logger()


@dataclass(slots=True)
class UpdateProjectGate(PostgresGate):
    async def __call__(self, project_id: UUID, data: dict) -> ProjectSchema:
        stmt = (
            update(Project)
            .where(Project.project_id == project_id)
            .values(**data)
            .returning(
                Project.project_id,
                Project.name,
                Project.description,
                Project.status,
                Project.owner,
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return self.retort.load(
            (result.mappings().fetchone()),
            ProjectSchema,
        )
