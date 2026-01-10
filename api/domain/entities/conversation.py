from typing import List, Optional
from datetime import datetime
from enum import Enum

class ConversationStatus(Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ConversationEntity:
    def __init__(
            self,
            id: str,
            user_id: str,
            title: str,
            status: ConversationStatus,
            created_at: datetime,
            updated_at: datetime,
            empathy_level: Optional[int] = 50,
            system_prompt: Optional[str] = None,
            metadata: Optional[dict] = None
    ):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.empathy_level = empathy_level or 50
        self.system_prompt = system_prompt
        self.metadata = metadata or {}

    @staticmethod
    def create(user_id: str, title: str, system_prompt: Optional[str] = None, empathy_level: Optional[int] = 50, metadata: Optional[dict] = None) -> ConversationEntity:
        now = datetime.now()
        return ConversationEntity(
            id = "",
            user_id=user_id,
            title=title,
            status=ConversationStatus.ACTIVE,
            system_prompt=system_prompt,
            empathy_level=empathy_level,
            metadata=metadata,
            created_at=now,
            updated_at=now
        )

        

