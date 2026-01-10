from abc import ABC, abstractmethod
from typing import Optional
from ..entities.user import UserEntity

class IUserRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: str) -> Optional[UserEntity]:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[UserEntity]:
        pass
    
    @abstractmethod
    def create(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def update(self, id: str, user_data: dict) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        pass