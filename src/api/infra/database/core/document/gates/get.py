from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from structlog import get_logger

from src.api.application.schemas.document import DocumentSchema
from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Document

logger = get_logger()


@dataclass(slots=True)
class GetDocumentGate(PostgresGate):
    async def __call__(self, document_id: UUID) -> DocumentSchema:
        stmt = select(
            Document.document_id,
            Document.project_id,
            Document.name,
            Document.link,
        ).where(Document.document_id == document_id)

        return self.retort.load(
            (await self.session.execute(stmt)).mappings().fetchone(),
            DocumentSchema,
        )
