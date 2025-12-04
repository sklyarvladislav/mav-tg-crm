from dataclasses import dataclass
from uuid import UUID

from src.api.infra.database.core.document.gates import (
    DeleteDocumentGate,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class DeleteDocumentUsecase:
    delete_document: DeleteDocumentGate

    async def __call__(self, document_id: UUID) -> bool:
        return await self.delete_document(document_id=document_id)
