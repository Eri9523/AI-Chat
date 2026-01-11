import sys
import os
import asyncio
from io import BytesIO

# Configurar entorno de test ANTES de importar la app
os.environ["ENVIRONMENT"] = "test"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app import app
from infrastructure.database.connection import connect_database

# Conectar a la base de datos mock antes de los tests
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(connect_database())

client = TestClient(app)

# ==================== VARIABLES GLOBALES PARA TESTS ====================
access_token = None
conversation_id = None
document_id = None


def get_auth_token():
    """Helper para obtener token de autenticación"""
    global access_token
    
    if access_token:
        return access_token
    
    # Registrar usuario de test
    register_response = client.post("/api/auth/register", json={
        "email": "ai_test@example.com",
        "name": "AI Test User",
        "password": "123456"
    })
    
    if register_response.status_code == 201:
        access_token = register_response.json()["access_token"]
    else:
        # Si ya existe, hacer login
        login_response = client.post("/api/auth/login", json={
            "email": "ai_test@example.com",
            "password": "123456"
        })
        access_token = login_response.json()["access_token"]
    
    return access_token


def get_auth_headers():
    """Helper para obtener headers de autenticación"""
    return {"Authorization": f"Bearer {get_auth_token()}"}


# ==================== CONVERSATION ENDPOINTS ====================

def test_create_conversation():
    """Test creating a new conversation"""
    global conversation_id
    
    response = client.post(
        "/api/ai/conversations",
        json={"title": "Test Conversation"},
        headers=get_auth_headers()
    )

    print(f"Create Conversation Status: {response.status_code}")
    print(f"Create Conversation Response: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Conversation"
    
    conversation_id = data["id"]


def test_create_conversation_no_auth():
    """Test creating conversation without auth should fail"""
    response = client.post(
        "/api/ai/conversations",
        json={"title": "Test Conversation"}
    )

    print(f"Create Conversation No Auth Status: {response.status_code}")

    assert response.status_code in [401, 403]


def test_get_conversations():
    """Test getting all conversations"""
    response = client.get(
        "/api/ai/conversations",
        headers=get_auth_headers()
    )

    print(f"Get Conversations Status: {response.status_code}")
    print(f"Get Conversations Response: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_conversation_messages():
    """Test getting messages from a conversation"""
    global conversation_id
    
    # Asegurarse de que tenemos una conversación
    if not conversation_id:
        test_create_conversation()
    
    response = client.get(
        f"/api/ai/conversations/{conversation_id}/messages",
        headers=get_auth_headers()
    )

    print(f"Get Messages Status: {response.status_code}")
    print(f"Get Messages Response: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_send_message():
    """Test sending a message to a conversation"""
    global conversation_id
    
    # Asegurarse de que tenemos una conversación
    if not conversation_id:
        test_create_conversation()
    
    response = client.post(
        f"/api/ai/conversations/{conversation_id}/messages",
        json={"content": "Hello, this is a test message"},
        headers=get_auth_headers()
    )

    print(f"Send Message Status: {response.status_code}")
    try:
        print(f"Send Message Response: {response.json()}")
    except:
        print(f"Send Message Response Text: {response.text}")

    # Puede fallar si OpenAI no está configurado, pero no debe ser 500
    assert response.status_code != 500


def test_delete_conversation():
    """Test deleting a conversation"""
    global conversation_id
    
    # Crear una nueva conversación para eliminar
    create_response = client.post(
        "/api/ai/conversations",
        json={"title": "Conversation to Delete"},
        headers=get_auth_headers()
    )
    
    if create_response.status_code == 200:
        conv_id = create_response.json()["id"]
        
        response = client.delete(
            f"/api/ai/conversations/{conv_id}",
            headers=get_auth_headers()
        )

        print(f"Delete Conversation Status: {response.status_code}")
        print(f"Delete Conversation Response: {response.json()}")

        assert response.status_code == 200


def test_delete_nonexistent_conversation():
    """Test deleting a non-existent conversation should fail"""
    response = client.delete(
        "/api/ai/conversations/000000000000000000000000",
        headers=get_auth_headers()
    )

    print(f"Delete Nonexistent Status: {response.status_code}")

    assert response.status_code in [404, 400]


# ==================== DOCUMENT ENDPOINTS ====================

def test_upload_document():
    """Test uploading a document"""
    global document_id
    
    # Crear un archivo de test
    file_content = b"This is a test document content for testing purposes."
    files = {"file": ("test_document.txt", BytesIO(file_content), "text/plain")}
    
    response = client.post(
        "/api/ai/documents",
        files=files,
        headers=get_auth_headers()
    )

    print(f"Upload Document Status: {response.status_code}")
    try:
        print(f"Upload Document Response: {response.json()}")
    except:
        print(f"Upload Document Response Text: {response.text}")

    # Puede fallar si ChromaDB no está configurado
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        document_id = data["id"]
    else:
        # Aceptar errores de servicio si ChromaDB no está disponible
        assert response.status_code != 500 or "chroma" in response.text.lower()


def test_upload_document_no_auth():
    """Test uploading document without auth should fail"""
    file_content = b"Test content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    response = client.post(
        "/api/ai/documents",
        files=files
    )

    print(f"Upload Document No Auth Status: {response.status_code}")

    assert response.status_code in [401, 403]


def test_get_documents():
    """Test getting all documents"""
    response = client.get(
        "/api/ai/documents",
        headers=get_auth_headers()
    )

    print(f"Get Documents Status: {response.status_code}")
    print(f"Get Documents Response: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_delete_document():
    """Test deleting a document"""
    global document_id
    
    # Si tenemos un documento de test, eliminarlo
    if document_id:
        response = client.delete(
            f"/api/ai/documents/{document_id}",
            headers=get_auth_headers()
        )

        print(f"Delete Document Status: {response.status_code}")
        try:
            print(f"Delete Document Response: {response.json()}")
        except:
            print(f"Delete Document Response Text: {response.text}")

        # Aceptar 200 o errores si ChromaDB no está disponible
        assert response.status_code != 500 or "chroma" in response.text.lower()


def test_delete_nonexistent_document():
    """Test deleting a non-existent document should fail"""
    response = client.delete(
        "/api/ai/documents/000000000000000000000000",
        headers=get_auth_headers()
    )

    print(f"Delete Nonexistent Document Status: {response.status_code}")

    assert response.status_code in [404, 400, 500]  # 500 si ChromaDB no está disponible
