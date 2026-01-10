from fastapi import UploadFile, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List

from application.use_cases.ai.create_conversation import CreateConversation
from application.use_cases.ai.send_message import SendMessage
from application.use_cases.ai.upload_document import UploadDocument

from infrastructure.database.repositories.mongo_conversation_repository import MongoConversationRepository
from infrastructure.database.repositories.mongo_message_repository import MongoMessageRepository
from infrastructure.database.repositories.mongo_document_repository import MongoDocumentRepository
from infrastructure.ai.openai_service import OpenAiService
from infrastructure.ai.chroma_service import ChromaService


class CreateConversationRequest(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = "You are a helpful AI assistant."
    empathy_level: Optional[int] = 50
    metadata: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Chat with pro gamer",
                "system_prompt": "You are a professional gamer",
                "empathy_level": 85
            }
        }

    def __init__(self, **data):
        super().__init__(**data)
        if self.empathy_level is not None:
            if not (1 <= self.empathy_level <= 100):
                raise ValueError("empathy_level must be between 1 and 100")

class SendMessageRequest(BaseModel):
    content: str


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    system_prompt: Optional[str] = None
    empathy_level: Optional[int] = 50
    created_at: str
    updated_at: str
    metadata: Optional[dict] = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    file_type: str
    file_size: int
    created_at: str


class ai_controller:
    def __init__(self):
        self.conversation_repository = MongoConversationRepository()
        self.message_repository = MongoMessageRepository()
        self.document_repository = MongoDocumentRepository()
        self.ai_service = OpenAiService()
        self.vector_service = ChromaService(self.ai_service)

    async def create_conversation(
        self, 
        user_id: str, 
        request: CreateConversationRequest
    ) -> ConversationResponse:
        from application.use_cases.ai.create_conversation import CreateConversationDto
        
        use_case = CreateConversation(self.conversation_repository)
        
        dto = CreateConversationDto(
            user_id=user_id,
            title=request.title,
            system_prompt=request.system_prompt,
            empathy_level=request.empathy_level,
            metadata=request.metadata
        )
        
        conversation_dict = await use_case.execute(dto)
        
        return ConversationResponse(
            id=conversation_dict["id"],
            user_id=conversation_dict["user_id"],
            title=conversation_dict["title"],
            created_at=conversation_dict["created_at"],
            updated_at=conversation_dict["updated_at"],
            empathy_level=conversation_dict.get("empathy_level"),
            system_prompt=conversation_dict.get("system_prompt"),
            metadata=conversation_dict.get("metadata", {}),

        )

    async def get_conversations(self, user_id: str) -> List[ConversationResponse]:
        conversations = await self.conversation_repository.find_by_user_id(user_id)
        
        return [
            ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                empathy_level=conv.empathy_level,
                system_prompt=conv.system_prompt,
                metadata=conv.metadata
            )
            for conv in conversations
        ]

    async def get_conversation_messages(
        self, 
        user_id: str, 
        conversation_id: str
    ) -> List[MessageResponse]:
        # Verify conversation belongs to user
        conversation = await self.conversation_repository.find_by_id(conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        messages = await self.message_repository.find_by_conversation_id(conversation_id)
        
        return [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat()
            )
            for msg in messages
        ]

    async def send_message(
        self, 
        user_id: str, 
        conversation_id: str, 
        request: SendMessageRequest
    ) -> MessageResponse:
        # Verify conversation belongs to user
        conversation = await self.conversation_repository.find_by_id(conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        use_case = SendMessage(
            message_repository=self.message_repository,
            conversation_repository=self.conversation_repository,
            ai_service=self.ai_service,
            vector_service=self.vector_service
        )
        
        from application.use_cases.ai.send_message import SendMessageDto
        
        dto = SendMessageDto(
            user_id=user_id,
            conversation_id=conversation_id,
            content=request.content,

        )
        
        ai_message_dict = await use_case.execute(dto)
        message_data = ai_message_dict["message"]
        
        return MessageResponse(
            id=message_data["id"],
            conversation_id=conversation_id,  # We know this from the request
            role=message_data["role"],
            content=message_data["content"],
            created_at=message_data["created_at"]
        )

    async def delete_conversation(self, user_id: str, conversation_id: str) -> dict:
        # Verify conversation belongs to user
        conversation = await self.conversation_repository.find_by_id(conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Delete messages first
        await self.message_repository.delete_by_conversation_id(conversation_id)
        
        # Delete conversation
        await self.conversation_repository.delete(conversation_id)
        
        return {"message": "Conversation deleted successfully"}

    async def upload_document(
        self, 
        user_id: str, 
        file: UploadFile
    ) -> DocumentResponse:
        # Validate file type
        allowed_types = ["application/pdf", "text/plain", "text/markdown"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {allowed_types}"
            )
        
        use_case = UploadDocument(
            document_repository=self.document_repository,
            vector_service=self.vector_service
        )
        
        document = await use_case.execute(
            user_id=user_id,
            file=file
        )
        
        return DocumentResponse(
            id=document.id,
            user_id=document.user_id,
            filename=document.filename,
            file_type=document.file_type,
            file_size=document.file_size,
            created_at=document.created_at.isoformat()
        )

    async def get_documents(self, user_id: str) -> List[DocumentResponse]:
        documents = await self.document_repository.find_by_user_id(user_id)
        
        return [
            DocumentResponse(
                id=doc.id,
                user_id=doc.user_id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                created_at=doc.created_at.isoformat()
            )
            for doc in documents
        ]

    async def delete_document(self, user_id: str, document_id: str) -> dict:
        document = await self.document_repository.find_by_id(document_id)
        if not document or document.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Delete vectors from ChromaDB
        if document.vector_ids:
            await self.vector_service.delete_vectors(document.vector_ids)
        
        # Delete document from database
        await self.document_repository.delete(document_id)
        
        return {"message": "Document deleted successfully"}


# Singleton instance
ai_controller = ai_controller()
