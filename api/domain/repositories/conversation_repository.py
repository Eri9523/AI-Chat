from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.conversation import ConversationEntity

class IConversationRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[ConversationEntity]:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str, limit: int = 20, offset: int = 0) -> List[ConversationEntity]:
        pass

    @abstractmethod
    def create(self, conversation: ConversationEntity) -> ConversationEntity:
        pass

    @abstractmethod
    def update(self, id: str, conversation_data: dict) -> Optional[ConversationEntity]:
        pass

    @abstractmethod
    def delete(self, id:str) -> bool:
        pass

    