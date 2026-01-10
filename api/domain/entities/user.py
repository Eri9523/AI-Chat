from typing import Optional
from datetime import datetime

class UserEntity:
    def __init__(
        self,
        id: str,
        email: str,
        name: str,
        password: str,
        created_at: datetime,
        updated_at: datetime,
        phone: Optional[str] = None,
        address: Optional[str] = None
    ):
        self.id = id
        self.email = email
        self.name = name
        self.password = password
        self.created_at = created_at
        self.updated_at = updated_at
        self.phone = phone
        self.address = address

    @staticmethod
    def create(
        email: str, 
        name: str, 
        hashed_password: str, 
        phone: Optional[str] = None, 
        address: Optional[str] = None
    ) -> "UserEntity":
        
        now = datetime.now()
        return UserEntity(
            id="",
            email=email,
            name=name,
            password=hashed_password,
            created_at=now,
            updated_at=now,
            phone=phone,
            address=address
        )