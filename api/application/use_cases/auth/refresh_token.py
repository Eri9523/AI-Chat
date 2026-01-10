from domain.repositories.user_repository import IUserRepository
from infrastructure.config.jwt import JwtService


class RefreshToken:
    def __init__(self, user_repository: IUserRepository, jwt_service: JwtService):
        self.user_repository = user_repository
        self.jwt_service = jwt_service
    
    def execute(self, refresh_token: str) -> dict:
        payload = self.jwt_service.verify_refresh_token(refresh_token)
        user = self.user_repository.find_by_id(payload["user_id"])
        if not user:
            raise Exception("User not found")
        
        token_payload = {
            "user_id": user.id,
            "email": user.email
        }

        new_access_token = self.jwt_service.generate_access_token(token_payload)
        new_refresh_token = self.jwt_service.generate_refresh_token(token_payload)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }