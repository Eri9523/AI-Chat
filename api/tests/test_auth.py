import sys
import os
import asyncio

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
test_user = {
    "email": "test@example.com",
    "name": "Test User",
    "password": "123456",
    "phone": "123456789",
    "address": "Test Address"
}
access_token = None
refresh_token_value = None


# ==================== AUTH ENDPOINTS ====================

def test_health():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register():
    """Test user registration"""
    global access_token, refresh_token_value
    
    response = client.post("/api/auth/register", json=test_user)
    
    print(f"Register Status: {response.status_code}")
    print(f"Register Response: {response.json()}")

    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == test_user["email"]
    
    # Guardar tokens para usar en otros tests
    access_token = data["access_token"]
    refresh_token_value = data["refresh_token"]


def test_register_duplicate_email():
    """Test registration with duplicate email should fail"""
    response = client.post("/api/auth/register", json=test_user)
    
    print(f"Duplicate Register Status: {response.status_code}")
    print(f"Duplicate Register Response: {response.json()}")
    
    # Debería fallar porque el email ya existe
    assert response.status_code in [400, 409]


def test_login():
    """Test user login"""
    global access_token, refresh_token_value
    
    response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })

    print(f"Login Status: {response.status_code}")
    print(f"Login Response: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == test_user["email"]
    
    # Actualizar tokens
    access_token = data["access_token"]
    refresh_token_value = data["refresh_token"]


def test_login_invalid_credentials():
    """Test login with invalid credentials should fail"""
    response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": "wrongpassword"
    })

    print(f"Invalid Login Status: {response.status_code}")
    print(f"Invalid Login Response: {response.json()}")

    assert response.status_code == 401


def test_get_current_user():
    """Test get current user info"""
    global access_token
    
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    print(f"Get Me Status: {response.status_code}")
    print(f"Get Me Response: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]


def test_get_current_user_no_token():
    """Test get current user without token should fail"""
    response = client.get("/api/auth/me")

    print(f"Get Me No Token Status: {response.status_code}")

    assert response.status_code in [401, 403]


def test_refresh_token():
    """Test refresh token"""
    global access_token, refresh_token_value
    
    response = client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token_value
    })

    print(f"Refresh Token Status: {response.status_code}")
    print(f"Refresh Token Response: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    
    # Actualizar access token
    access_token = data["access_token"]


def test_logout():
    """Test user logout"""
    global access_token
    
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    print(f"Logout Status: {response.status_code}")
    print(f"Logout Response: {response.json()}")

    assert response.status_code == 200
