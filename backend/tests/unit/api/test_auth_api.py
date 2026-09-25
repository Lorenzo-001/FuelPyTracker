"""
Test unitari per il Router Auth di FastAPI (/api/auth) e i modelli Pydantic.
Verifica i contratti dati, la validazione, il login, la registrazione e il profilo utente.
"""
import pytest
import jwt
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.api.server import app
from src.api.config import DEMO_USER_ID, DEMO_USER_EMAIL

@pytest.fixture
def client():
    return TestClient(app)


# =============================================================================
# TEST: Validazione Pydantic
# =============================================================================

def test_login_validation_invalid_email(client):
    """Verifica che un'email malformata venga rifiutata con HTTP 422."""
    response = client.post("/api/auth/login", json={
        "email": "not-an-email",
        "password": "valid_password123"
    })
    assert response.status_code == 422


def test_login_validation_short_password(client):
    """Verifica che una password inferiore a 6 caratteri venga rifiutata con HTTP 422."""
    response = client.post("/api/auth/login", json={
        "email": "valid@example.com",
        "password": "123"
    })
    assert response.status_code == 422


# =============================================================================
# TEST: POST /api/auth/login
# =============================================================================

def test_login_demo_mode_success(client):
    """Verifica il successo immediato del login in ambiente Demo."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=True):
        response = client.post("/api/auth/login", json={
            "email": "demo@fuelpytracker.com",
            "password": "any_password"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["is_demo"] is True
        assert data["user"]["id"] == DEMO_USER_ID


def test_login_failed_in_production(client):
    """Verifica che credenziali errate restituiscano HTTP 401."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=False), \
         patch("src.api.routers.auth.is_local_sqlite", return_value=False), \
         patch("src.api.routers.auth.DEMO_MODE", False), \
         patch("src.services.auth.auth_service.sign_in", side_effect=Exception("Invalid login credentials")):
        response = client.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "wrong_password"
        })
        assert response.status_code == 401


# =============================================================================
# TEST: POST /api/auth/register
# =============================================================================

def test_register_demo_mode_success(client):
    """Verifica la risposta simulata di registrazione in modalità Demo."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=True):
        response = client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "password": "securePassword123!"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True


def test_register_error_handling(client):
    """Verifica la gestione degli errori durante la registrazione."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=False), \
         patch("src.api.routers.auth.is_local_sqlite", return_value=False), \
         patch("src.api.routers.auth.DEMO_MODE", False), \
         patch("src.services.auth.auth_service.sign_up", side_effect=Exception("User already registered")):
        response = client.post("/api/auth/register", json={
            "email": "existing@example.com",
            "password": "securePassword123!"
        })
        assert response.status_code == 400


# =============================================================================
# TEST: POST /api/auth/logout
# =============================================================================

def test_logout(client):
    """Verifica l'endpoint di logout."""
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True


# =============================================================================
# TEST: GET /api/auth/me
# =============================================================================

def test_get_me_demo_mode(client):
    """Verifica che /api/auth/me restituisca l'utente demo in ambiente demo."""
    with patch("src.api.deps.is_demo_mode", return_value=True):
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == DEMO_USER_ID
        assert data["is_demo"] is True


def test_get_me_with_jwt_token(client):
    """Verifica che /api/auth/me risolva correttamente l'utente da un token Bearer."""
    custom_uid = "user-real-uuid-777"
    token = jwt.encode({"sub": custom_uid, "email": "real@example.com"}, "secret", algorithm="HS256")
    
    with patch("src.api.deps.is_demo_mode", return_value=False), \
         patch("src.api.deps.is_local_sqlite", return_value=False), \
         patch("src.api.deps.DEMO_MODE", False), \
         patch("src.services.auth.auth_service.get_client", return_value=None):
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == custom_uid
        assert data["is_demo"] is False


def test_get_me_unauthorized(client):
    """Verifica che /api/auth/me sollevi 401 in assenza di credenziali fuori da demo."""
    with patch("src.api.deps.is_demo_mode", return_value=False), \
         patch("src.api.deps.is_local_sqlite", return_value=False), \
         patch("src.api.deps.DEMO_MODE", False):
        response = client.get("/api/auth/me")
        assert response.status_code == 401


# =============================================================================
# TEST: POST /api/auth/reset-password
# =============================================================================

def test_reset_password_demo(client):
    """Verifica il comportamento di recupero password in demo."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=True):
        response = client.post("/api/auth/reset-password", json={
            "email": "demo@example.com"
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
