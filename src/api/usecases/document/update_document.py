from dataclasses import asdict, dataclass
from uuid import UUID

from src.api.application.schemas.document import (
    DocumentSchema,
    DocumentUpdateSchema,
)
from src.api.infra.database.core.document.gates.update import (
    UpdateDocumentGate,
)


@dataclass(slots=True, frozen=True, kw_only=True)
class UpdateDocumentUsecase:
    update_document: UpdateDocumentGate

    async def __call__(
        self, document_id: UUID, data: DocumentUpdateSchema
    ) -> DocumentSchema:
        update_data = {k: v for k, v in asdict(data).items() if v is not None}
        return await self.update_document(
            document_id=document_id, data=update_data
        )
