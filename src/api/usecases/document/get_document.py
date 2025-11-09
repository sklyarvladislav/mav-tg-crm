from dataclasses import dataclass
from uuid import UUID

from src.api.application.schemas.document import DocumentSchema
from src.api.infra.database.core.document.gates.get import GetDocumentGate


@dataclass(slots=True, frozen=True, kw_only=True)
class GetDocumentUsecase:
    get_document: GetDocumentGate

    async def __call__(self, document_id: UUID) -> DocumentSchema:
        document: DocumentSchema = await self.get_document(
            document_id=document_id
        )

        return DocumentSchema(
            document_id=document.document_id,
            project_id=document.project_id,
            name=document.name,
            link=document.link,
        )
