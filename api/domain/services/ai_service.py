from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from ..entities.message import MessageEntity

class IAIService(ABC):
    @abstractmethod
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool= False
    ) -> str | AsyncGenerator[str, None]:
        pass

    @abstractmethod
    async def generate_embeedings(self, text: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass

    