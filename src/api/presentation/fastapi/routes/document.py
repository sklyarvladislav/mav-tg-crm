from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from src.api.application.schemas.document import (
    DocumentSchema,
    DocumentUpdateSchema,
)
from src.api.infra.database.common import CreateGate
from src.api.infra.database.tables.document import Document
from src.api.usecases.document.delete_document import DeleteDocumentUsecase
from src.api.usecases.document.get_document import GetDocumentUsecase
from src.api.usecases.document.update_document import UpdateDocumentUsecase

logger = get_logger()
router = APIRouter(route_class=DishkaRoute)


@router.post("")
async def create_document(
    request: DocumentSchema,
    session: FromDishka[AsyncSession],
    create: FromDishka[CreateGate[Document, DocumentSchema]],
) -> DocumentSchema:
    async with session.begin():
        created = await create.returning()(
            DocumentSchema(
                document_id=request.document_id,
                project_id=request.project_id,
                name=request.name,
                link=request.link,
            )
        )

    return DocumentSchema(
        document_id=created.document_id,
        project_id=created.project_id,
        name=created.name,
        link=created.link,
    )


@router.get("/{document_id}")
async def get_document(
    usecase: FromDishka[GetDocumentUsecase],
    document_id: UUID,
) -> DocumentSchema:
    return await usecase(document_id=document_id)


@router.get("/{project_id}/documents")
async def get_project_documents(
    project_id: UUID,
    session: FromDishka[AsyncSession],
) -> list[DocumentSchema]:
    async with session.begin():
        result = await session.execute(
            select(Document).where(Document.project_id == project_id)
        )
        documents = result.scalars().all()

    return [
        DocumentSchema(
            document_id=doc.document_id,
            project_id=doc.project_id,
            name=doc.name,
            link=doc.link,
        )
        for doc in documents
    ]


@router.delete("/{document_id}")
async def delete_document(
    usecase: FromDishka[DeleteDocumentUsecase],
    document_id: UUID,
) -> dict:
    await usecase(document_id=document_id)
    return {"200": "document removed"}


@router.patch("/{document_id}")
async def update_document(
    usecase: FromDishka[UpdateDocumentUsecase],
    document_id: UUID,
    data: DocumentUpdateSchema,
) -> DocumentSchema:
    return await usecase(document_id=document_id, data=data)
