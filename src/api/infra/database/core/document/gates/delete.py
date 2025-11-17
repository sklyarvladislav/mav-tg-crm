from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select

from src.api.infra.database.common import PostgresGate
from src.api.infra.database.tables import Document


@dataclass(slots=True)
class DeleteDocumentGate(PostgresGate):
    async def __call__(self, document_id: UUID) -> bool:
        stmt_select = select(Document).where(
            Document.document_id == document_id
        )
        document = (
            await self.session.execute(stmt_select)
        ).scalar_one_or_none()

        if document is None:
            return False

        stmt_delete = delete(Document).where(
            Document.document_id == document_id
        )
        await self.session.execute(stmt_delete)
        await self.session.commit()
        return True
