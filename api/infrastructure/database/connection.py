import os
import mongoengine
from infrastructure.config.environment import config


async def connect_database():
    """Conectar a la base de datos MongoDB"""
    try:
        # Si estamos en tests, usar mongomock
        if os.getenv("ENVIRONMENT") == "test":
            import mongomock
            mongoengine.connect(
                'test_db',
                mongo_client_class=mongomock.MongoClient
            )
            print("Connected to MongoDB mock for testing")
        else:
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
