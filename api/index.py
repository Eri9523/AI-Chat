import uvicorn
from infrastructure.config.environment import config
from app import app


if __name__ == "__main__":
    uvicorn.run(
        "index:app",
        host="0.0.0.0",
        port=int(config["port"] or 3000),
        reload=config["env"] == "development"
    )