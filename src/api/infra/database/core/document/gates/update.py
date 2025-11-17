from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import update
from structlog import get_logger

from src.api.application.schemas.document import DocumentSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Document

logger = get_logger()


@dataclass(slots=True)
class UpdateDocumentGate(PostgresGate):
    async def __call__(self, document_id: UUID, data: dict) -> DocumentSchema:
        stmt = (
            update(Document)
            .where(Document.document_id == document_id)
            .values(**data)
            .returning(
                Document.document_id,
                Document.project_id,
                Document.name,
                Document.link,
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return self.retort.load(
            (result.mappings().fetchone()),
            DocumentSchema,
        )
