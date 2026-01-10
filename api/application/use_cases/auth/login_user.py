import bcrypt
from typing import Optional
from domain.repositories.user_repository import IUserRepository
from infrastructure.config.jwt import JwtService


class LoginUserDto:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password


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


class LoginUser:
    def __init__(self, user_repository: IUserRepository, jwt_service: JwtService):
        self.user_repository = user_repository
        self.jwt_service = jwt_service

    def execute(self, dto: LoginUserDto) -> dict:
        user = self.user_repository.find_by_email(dto.email)
        if not user:
            raise Exception("Invalid credentials")
        
        if not bcrypt.checkpw(dto.password.encode(), user.password.encode()):
            raise Exception("Invalid credentials")

        token_payload = {
            "user_id": user.id,
            "email": user.email
        }

        access_token = self.jwt_service.generate_access_token(token_payload)
        refresh_token = self.jwt_service.generate_refresh_token(token_payload)

        user_data = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        }

        auth_response = AuthResponse(user_data, access_token, refresh_token)
        return auth_response.to_dict()