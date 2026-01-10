from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IVectorService(ABC):
    @abstractmethod
    async def store_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        pass

    @abstractmethod
    async def search_similar(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete_documents(self, ids: List[str]) -> bool:
        pass

    @abstractmethod
    async def get_collection_info(self) -> Dict[str, Any]:
        pass
