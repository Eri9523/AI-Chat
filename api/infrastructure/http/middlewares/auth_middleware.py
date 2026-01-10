from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from infrastructure.config.jwt import JwtService

security = HTTPBearer()
jwt_service = JwtService()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """FastAPI dependency para autenticación JWT"""
    try:
        token = credentials.credentials
        payload = jwt_service.verify_access_token(token)
        return payload
    except Exception as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """FastAPI dependency para autenticación JWT opcional"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt_service.verify_access_token(token)
        return payload
    except Exception:
        return None
