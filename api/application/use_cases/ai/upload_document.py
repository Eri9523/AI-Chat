import asyncio
from typing import List
from domain.entities.document import DocumentEntity, DocumentType, ProcessingStatus
from domain.repositories.document_repository import IDocumentRepository
from domain.services.ai_service import IAIService
from domain.services.vector_service import IVectorService

class UploadDocumentDto:
    def __init__(
        self,
        user_id:str,
        filename: str,
        content: str,
        document_type: DocumentType,
        file_size: int,
        metadata: dict = None
    ):
        self.user_id=user_id
        self.filename=filename
        self.content=content
        self.document_type=document_type
        self.file_size=file_size
        self.metadata=metadata

class UploadDocument:
    def __init__(
        self,
        document_repository: IDocumentRepository,
        ai_service: IAIService,
        vector_service: IVectorService
    ):
        self.document_repository = document_repository
        self.ai_service = ai_service
        self.vector_service = vector_service

    async def execute(self, dto: UploadDocumentDto) -> dict:
        document = DocumentEntity.create(
            user_id=dto.user_id,
            filename=dto.filename,
            content=dto.content,
            document_type=dto.document_type,
            file_size=dto.file_size,
            metadata=dto.metadata,
        )

        saved_document = await self.document_repository.create(document)

        asyncio.create_task(self._process_document(saved_document))

        return{
            "id":saved_document.id,
            "filename":saved_document.filename,
            "status":saved_document.status.value,
            "created_at":saved_document.created_at.isoformat()
        }
    
    async def _process_document(self, document:DocumentEntity):
        try:
            await self.document_repository.update(
                document.id,
                {"status": ProcessingStatus.PROCESSING}
            )

            chunks = self._split_text(document.content)

            metadatas = []

            for i, chunk in enumerate(chunks):
                metadata = {
                    "document_id": document.id,
                    "user_id": document.user_id,
                    "filanem": document.filename,
                    "chunk_index": i,
                    "document_type": document.document_type.value
                }
                metadatas.append(metadata)

            vector_ids = await self.vector_service.store_documents(
                documents=chunks,
                metadatas=metadatas
            )

            await self.document_repository.update(
                document.id,
                {
                    "status": ProcessingStatus.COMPLETED,
                    "vector_ids": vector_ids
                }
            )
        except Exception as error:

            await self.document_repository.update(
                document.id,
                {
                    "status": ProcessingStatus.ERROR,
                    "error_message": str(error)
                }
            )

    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Divide text in chunks using overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Find last space
            if end < len(text):
                last_space = chunk.rfind(' ')
                if last_space > chunk_size // 2:  # Only if space is in second half
                    chunk = chunk[:last_space]
                    end = start + last_space
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
                
        return [chunk for chunk in chunks if chunk]  # Filter empty chunks

    

