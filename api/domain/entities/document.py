from typing import Optional, List
from datetime import datetime
from enum import Enum

class DocumentType(Enum):
    TEXT = "text"
    PDF = "pdf"
    MARKDOWN = "markdown"
    HTML = "html"

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class DocumentEntity:
    def __init__(
        self, 
        id: str, 
        user_id: str, 
        filename: str, 
        content: str, 
        document_type: DocumentType, 
        status: ProcessingStatus, 
        file_size: int, 
        created_at: datetime, 
        updated_at: datetime, 
        vector_ids: Optional[List[str]] = None, 
        metadata: Optional[dict] = None, 
        error_message: Optional[str] = None
    ):
        self.id = id
        self.user_id= user_id
        self.filename = filename
        self.content = content
        self.document_type = document_type
        self.status = status
        self.file_size = file_size
        self.created_at = created_at
        self.updated_at = updated_at
        self.vector_ids = vector_ids
        self.metadata = metadata
        self.error_message = error_message
    
    @staticmethod
    def create(
        user_id: str,
        filename: str,
        content: str,
        document_type: DocumentType,
        file_size: int,
        metadata: Optional[dict] = None
    ) -> DocumentEntity:
        now = datetime.now()
        return DocumentEntity(
            id="",
            user_id=user_id,
            filename=filename,
            content=content,
            document_type=document_type,
            status=ProcessingStatus.PENDING,
            file_size=file_size,
            created_at=now,
            updated_at=now,
            metadata=metadata
        )
