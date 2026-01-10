from fastapi import APIRouter, Depends
from infrastructure.http.controllers.auth_controller import (
    auth_controller, 
    RegisterRequest, 
    LoginRequest, 
    RefreshTokenRequest
)
from infrastructure.http.middlewares.auth_middleware import get_current_user

router = APIRouter()


@router.post("/register", status_code=201)
async def register(request: RegisterRequest):
    return await auth_controller.register(request)


@router.post("/login")
async def login(request: LoginRequest):
    return await auth_controller.login(request)


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    return await auth_controller.refresh_token(request)


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return await auth_controller.get_current_user(current_user)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    return await auth_controller.logout()