from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.document import DocumentEntity

class IDocumentRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[DocumentEntity]:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> List[DocumentEntity]:
        pass

    @abstractmethod
    def create(self, document: DocumentEntity) -> DocumentEntity:
        pass

    @abstractmethod
    def update(self, id: str, document_data: dict) -> Optional[DocumentEntity]:
        pass

    @abstractmethod
    def delete(self, id:str) -> bool:
        pass

    