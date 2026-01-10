import mongoengine
from infrastructure.config.environment import config


async def connect_database():
    """Conectar a la base de datos MongoDB"""
    try:
        mongodb_uri = config["mongodb"]["uri"]
        if not mongodb_uri:
            raise Exception("MONGODB_URI not defined in environment")
        
        # Conectar a MongoDB usando mongoengine
        mongoengine.connect(host=mongodb_uri)
        print("Connected to MongoDB successfully")
        
    except Exception as error:
        print(f"Error connecting to database: {error}")
        raise


def disconnect_database():
    """Desconectar de la base de datos MongoDB"""
    mongoengine.disconnect()
    print("Disconnected from MongoDB")