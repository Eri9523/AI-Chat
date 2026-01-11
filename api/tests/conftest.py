import pytest
import os
import asyncio
from typing import AsyncGenerator
import logging

# Configure test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["LOG_LEVEL"] = "WARNING"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def clean_db() -> AsyncGenerator[None, None]:
    """Clean the test database before and after each test."""
    try:
        # Use mongomock for tests (in-memory)
        from mongomock_motor import AsyncMongoMockClient
        client = AsyncMongoMockClient()
    except ImportError:
        # Fallback to real MongoDB
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient("mongodb://localhost:27017/ai_chatbot_test")
    
    db = client.ai_chatbot_test
    
    yield
    
    # Clean after test
    collections = await db.list_collection_names()
    for collection_name in collections:
        await db[collection_name].delete_many({})
    
    client.close()
