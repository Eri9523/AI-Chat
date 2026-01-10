from typing import List, Optional
from bson import ObjectId
from domain.repositories.document_repository import IDocumentRepository
from domain.entities.document import DocumentEntity
from infrastructure.database.models.document_model import DocumentModel


class MongoDocumentRepository(IDocumentRepository):
    async def create(self, document: DocumentEntity) -> DocumentEntity:
        document_model = DocumentModel(
            user_id=document.user_id,
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            vector_ids=document.vector_ids,
            created_at=document.created_at
        )
        document_model.save()
        document.id = str(document_model.id)
        return document

    async def find_by_id(self, document_id: str) -> Optional[DocumentEntity]:
        document_model = DocumentModel.objects(id=document_id).first()
        if not document_model:
            return None
        return self._to_entity(document_model)

    async def find_by_user_id(self, user_id: str) -> List[DocumentEntity]:
        documents = DocumentModel.objects(user_id=user_id).order_by('-created_at')
        return [self._to_entity(d) for d in documents]

    async def update(self, id: str, document_data: dict) -> Optional[DocumentEntity]:
        document = DocumentModel.objects(id=id).first()
        if not document:
            return None
        for key, value in document_data.items():
            if hasattr(document, key):
                setattr(document, key, value)
        document.save()
        return self._to_entity(document)

    async def delete(self, document_id: str) -> bool:
        result = DocumentModel.objects(id=document_id).delete()
        return result > 0

    def _to_entity(self, model: DocumentModel) -> DocumentEntity:
        return DocumentEntity(
            id=str(model.id),
            user_id=str(model.user_id),
            filename=model.filename,
            file_type=model.file_type,
            file_size=model.file_size,
            vector_ids=model.vector_ids,
            created_at=model.created_at
        )
