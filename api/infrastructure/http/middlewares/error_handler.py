from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from infrastructure.config.environment import config
import traceback
from typing import Dict, Any


def add_error_handlers(app: FastAPI):
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        print(f"Error: {exc}")
        
        response_content: Dict[str, Any] = {
            "message": "Internal server error"
        }
        
        # Solo incluir stack trace en desarrollo
        if config["env"] == "development":
            response_content["stack"] = traceback.format_exc()
        
        return JSONResponse(
            status_code=500,
            content=response_content
        )