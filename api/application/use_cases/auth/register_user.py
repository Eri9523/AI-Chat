import bcrypt
from typing import Optional
from domain.entities.user import UserEntity
from domain.repositories.user_repository import IUserRepository
from infrastructure.config.jwt import JwtService


class RegisterUserDto:
    def __init__(
            self, email: str, 
            name: str, 
            password: str, 
            phone: Optional[str] = None, 
            address: Optional[str] = None
        ):
        self.email = email
        self.name = name
        self.password = password
        self.phone = phone
        self.address = address


class AuthResponse:
    def __init__(self, user: dict, access_token: str, refresh_token: str):
        self.user = user
        self.access_token = access_token
        self.refresh_token = refresh_token
        
    def to_dict(self) -> dict:
        return {
            "user": self.user,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token
        }


class RegisterUser:
    def __init__(self, user_repository: IUserRepository, jwt_service: JwtService):
        self.user_repository = user_repository
        self.jwt_service = jwt_service

    def execute(self, dto: RegisterUserDto) -> dict:
        existing_user = self.user_repository.find_by_email(dto.email)
        if existing_user:
            raise Exception("User with this email already exists")

        hashed_password = bcrypt.hashpw(dto.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user_entity = UserEntity.create(
            email=dto.email,
            name=dto.name,
            hashed_password=hashed_password,
            phone=dto.phone,
            address=dto.address
        )

        saved_user = self.user_repository.create(user_entity)

        token_payload = {
            "user_id": saved_user.id,
            "email": saved_user.email
        }

        access_token = self.jwt_service.generate_access_token(token_payload)
        refresh_token = self.jwt_service.generate_refresh_token(token_payload)

        user_dict = {
            "id": saved_user.id,
            "email": saved_user.email,
            "name": saved_user.name,
            "phone": saved_user.phone,
            "created_at": saved_user.created_at.isoformat(),
            "updated_at": saved_user.updated_at.isoformat()
        }

        auth_response = AuthResponse(user_dict, access_token, refresh_token)
        return auth_response.to_dict()

