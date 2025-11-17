from dataclasses import dataclass
from enum import Enum
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
        for k, v in data.items():
            if isinstance(v, Enum):
                data[k] = v.value

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

        row = result.mappings().fetchone()
        if row is not None:
            row = dict(row)
            for k, v in row.items():
                if isinstance(v, Enum):
                    row[k] = v.value

        return self.retort.load(
            row,
            ProjectSchema,
        )
