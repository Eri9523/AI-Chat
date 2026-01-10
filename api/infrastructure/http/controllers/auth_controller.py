from fastapi import HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from application.use_cases.auth.register_user import RegisterUser, RegisterUserDto
from application.use_cases.auth.login_user import LoginUser, LoginUserDto
from application.use_cases.auth.refresh_token import RefreshToken
from infrastructure.database.repositories.mongo_user_repository import MongoUserRepository
from infrastructure.config.jwt import JwtService
from infrastructure.http.middlewares.auth_middleware import get_current_user


user_repository = MongoUserRepository()
jwt_service = JwtService()


class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: str
    updated_at: str


class AuthController:
    
    @staticmethod
    async def register(request: RegisterRequest):
        try:
            register_user = RegisterUser(user_repository, jwt_service)
            dto = RegisterUserDto(
                email=request.email,
                name=request.name,
                password=request.password,
                phone=request.phone,
                address=request.address
            )
            result = register_user.execute(dto)
            return result
        except Exception as error:
            raise HTTPException(status_code=400, detail=str(error))
    
    @staticmethod
    async def login(request: LoginRequest):
        try:
            login_user = LoginUser(user_repository, jwt_service)
            dto = LoginUserDto(email=request.email, password=request.password)
            result = login_user.execute(dto)
            return result
        except Exception as error:
            raise HTTPException(status_code=401, detail=str(error))
    
    @staticmethod
    async def refresh_token(request: RefreshTokenRequest):
        try:
            refresh_token_use_case = RefreshToken(user_repository, jwt_service)
            result = refresh_token_use_case.execute(request.refresh_token)
            return result
        except Exception as error:
            raise HTTPException(status_code=401, detail=str(error))
    
    @staticmethod
    async def get_current_user(current_user: dict = Depends(get_current_user)):
        try:
            user = user_repository.find_by_id(current_user["user_id"])
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "phone": user.phone,
                "address": user.address,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }
        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))
    
    @staticmethod
    async def logout():
        # En un sistema JWT sin estado, el logout se maneja del lado del cliente
        return {"message": "Logged out successfully"}


auth_controller = AuthController()
