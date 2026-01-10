from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(Enum):
    USER="user"
    ASSISTANT="assistant"
    SYSTEM="system"

class MessageStatus(Enum):
    PENDING="pending"
    COMPLETED="completed"
    ERROR="error"

class MessageEntity:
    def __init__(
        self, 
        id: str, 
        conversation_id: str, 
        role: MessageRole, 
        content: str, 
        status: MessageStatus, 
        created_at: datetime, 
        updated_at: datetime, 
        token_count: Optional[int] = None, 
        metadata: Optional[Dict[str, Any]] = None, 
        error_message: Optional[str] = None
        ):
        self.id = id
        self.conversation_id = conversation_id
        self.role = role
        self.content = content
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.token_count = token_count
        self.metadata = metadata or {}
        self.error_message = error_message

    @staticmethod
    def create_user_message(
        conversation_id: str,
        content:str
    ) -> MessageEntity:
        now = datetime.now()
        return MessageEntity(
            id= "",
            conversation_id=conversation_id,
            role = MessageRole.USER,
            content=content,
            status=MessageStatus.COMPLETED,
            created_at=now,
            updated_at=now
        )
    
    @staticmethod
    def create_assistant_message(
        conversation_id: str,
        content:str,
        status: MessageStatus = MessageStatus.PENDING
    ) -> MessageEntity:
        now = datetime.now()
        return MessageEntity(
            id= "",
            conversation_id=conversation_id,
            role = MessageRole.ASSISTANT,
            content=content,
            status=status,
            created_at=now,
            updated_at=now
        )
