import jwt
from datetime import datetime, timedelta
from infrastructure.config.environment import config


class JwtService:
    @staticmethod
    def generate_access_token(payload: dict) -> str:
        expires_in = config["jwt"]["expires_in"]
        secret = config["jwt"]["secret"]
        if not secret:
            raise Exception("JWT_SECRET not defined in environment")
        if not expires_in:
            raise Exception("JWT_EXPIRES_IN not defined in environment")
        exp = datetime.now() + timedelta(seconds=int(expires_in))
        payload_with_exp = {**payload, "exp": exp}
        return jwt.encode(payload_with_exp, secret, algorithm="HS256")
    
    @staticmethod
    def generate_refresh_token(payload: dict) -> str:
        refresh_expires_in = config["jwt"]["refresh_expires_in"]
        refresh_secret = config["jwt"]["refresh_secret"]
        if not refresh_secret:
            raise Exception("JWT_REFRESH_SECRET not defined in environment")
        if not refresh_expires_in:
            raise Exception("JWT_REFRESH_EXPIRES_IN not defined in environment")
        exp = datetime.now() + timedelta(seconds=int(refresh_expires_in))
        payload_with_exp = {**payload, "exp": exp}
        return jwt.encode(payload_with_exp, refresh_secret, algorithm="HS256")
    
    @staticmethod
    def verify_access_token(token: str) -> dict:
        secret = config["jwt"]["secret"]
        if not secret:
            raise Exception("JWT_SECRET not defined in environment")
        try:
            return jwt.decode(token, secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
        
    @staticmethod
    def verify_refresh_token(token: str) -> dict:
        refresh_secret = config["jwt"]["refresh_secret"]
        if not refresh_secret:
            raise Exception("JWT_REFRESH_SECRET not defined in environment")
        try:
            return jwt.decode(token, refresh_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise Exception("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid refresh token")