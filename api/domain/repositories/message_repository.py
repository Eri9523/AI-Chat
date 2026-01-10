from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.message import MessageEntity

class IMessageRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[MessageEntity]:
        pass

    @abstractmethod
    def find_by_conversation_id(self, conversation_id: str) -> List[MessageEntity]:
        pass

    @abstractmethod
    def create(self, message: MessageEntity) -> MessageEntity:
        pass

    @abstractmethod
    def update(self, id: str, message_data: dict) -> Optional[MessageEntity]:
        pass

    @abstractmethod
    def delete(self, id:str) -> bool:
        pass

    