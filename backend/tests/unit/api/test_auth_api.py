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
        assert "Se l'indirizzo email è associato a un account" in response.json()["message"]


def test_reset_password_anti_enumeration(client):
    """Verifica la protezione anti-enumeration (risponde sempre 200 sia che l'email esista o meno)."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=False), \
         patch("src.api.routers.auth.is_local_sqlite", return_value=False), \
         patch("src.api.routers.auth.DEMO_MODE", False), \
         patch("src.services.auth.auth_service.send_password_reset_email", return_value=(False, "User not found")):
        response = client.post("/api/auth/reset-password", json={
            "email": "nonexistent@example.com"
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "Se l'indirizzo email è associato a un account" in response.json()["message"]


# =============================================================================
# TEST: POST /api/auth/update-password-recovery
# =============================================================================

def test_update_password_recovery_validation(client):
    """Verifica la validazione Pydantic per password troppo corta (< 8 car) o token mancante."""
    # Password troppo corta
    res1 = client.post("/api/auth/update-password-recovery", json={
        "access_token": "valid_token_1234567890",
        "new_password": "short"
    })
    assert res1.status_code == 422

    # Token troppo corto
    res2 = client.post("/api/auth/update-password-recovery", json={
        "access_token": "short",
        "new_password": "validPassword123"
    })
    assert res2.status_code == 422


def test_update_password_recovery_demo(client):
    """Verifica che in ambiente Demo il reset password ritorni esito positivo simulato."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=True):
        res = client.post("/api/auth/update-password-recovery", json={
            "access_token": "recovery-jwt-token-123456",
            "new_password": "newSecurePassword123"
        })
        assert res.status_code == 200
        assert res.json()["success"] is True
        assert "Demo" in res.json()["message"]


def test_update_password_recovery_success(client):
    """Verifica il successo dell'aggiornamento con token valido."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=False), \
         patch("src.api.routers.auth.is_local_sqlite", return_value=False), \
         patch("src.api.routers.auth.DEMO_MODE", False), \
         patch("src.services.auth.auth_service.update_password_with_recovery_token", return_value=(True, "Password aggiornata con successo!")):
        res = client.post("/api/auth/update-password-recovery", json={
            "access_token": "valid-recovery-token-12345678",
            "new_password": "brandNewPassword123"
        })
        assert res.status_code == 200
        assert res.json()["success"] is True


def test_update_password_recovery_invalid_token(client):
    """Verifica errore HTTP 400 se il token è scaduto o non valido."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=False), \
         patch("src.api.routers.auth.is_local_sqlite", return_value=False), \
         patch("src.api.routers.auth.DEMO_MODE", False), \
         patch("src.services.auth.auth_service.update_password_with_recovery_token", return_value=(False, "Il link di recupero è scaduto o non è valido.")):
        res = client.post("/api/auth/update-password-recovery", json={
            "access_token": "expired-token-1234567890",
            "new_password": "brandNewPassword123"
        })
        assert res.status_code == 400
        assert "scaduto o non è valido" in res.json()["detail"]


# =============================================================================
# TEST: POST /api/auth/change-password
# =============================================================================

def test_change_password_identical_error(client):
    """Verifica rifiuto con HTTP 400 se la nuova password coincide con la vecchia."""
    res = client.post("/api/auth/change-password", json={
        "current_password": "samePassword123",
        "new_password": "samePassword123"
    }, headers={"X-User-Id": "some-user"})
    assert res.status_code == 400
    assert "diversa da quella attuale" in res.json()["detail"]


def test_change_password_demo(client):
    """Verifica che in ambiente demo risponda con esito positivo simulato."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=True):
        res = client.post("/api/auth/change-password", json={
            "current_password": "oldPassword123",
            "new_password": "newSecurePassword123"
        })
        assert res.status_code == 200
        assert res.json()["success"] is True
        assert "Demo" in res.json()["message"]


def test_change_password_success(client):
    """Verifica successo del cambio password per utente reale."""
    dummy_jwt = jwt.encode({"sub": "real-uuid-1", "email": "test@domain.com"}, "secret", algorithm="HS256")
    with patch("src.api.routers.auth.is_demo_mode", return_value=False), \
         patch("src.api.routers.auth.is_local_sqlite", return_value=False), \
         patch("src.api.routers.auth.DEMO_MODE", False), \
         patch("src.services.auth.auth_service.update_user_password_secure", return_value=(True, "Password aggiornata con successo!")):
        res = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "oldPassword123",
                "new_password": "brandNewPassword123"
            },
            headers={"Authorization": f"Bearer {dummy_jwt}"}
        )
        assert res.status_code == 200
        assert res.json()["success"] is True


def test_change_password_wrong_current(client):
    """Verifica errore HTTP 400 se la password attuale è errata."""
    dummy_jwt = jwt.encode({"sub": "real-uuid-1", "email": "test@domain.com"}, "secret", algorithm="HS256")
    with patch("src.api.routers.auth.is_demo_mode", return_value=False), \
         patch("src.api.routers.auth.is_local_sqlite", return_value=False), \
         patch("src.api.routers.auth.DEMO_MODE", False), \
         patch("src.services.auth.auth_service.update_user_password_secure", return_value=(False, "La password attuale inserita non è corretta.")):
        res = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "wrongOldPassword",
                "new_password": "brandNewPassword123"
            },
            headers={"Authorization": f"Bearer {dummy_jwt}"}
        )
        assert res.status_code == 400
        assert "non è corretta" in res.json()["detail"]


# =============================================================================
# TEST: POST /api/auth/change-email
# =============================================================================

def test_change_email_demo(client):
    """Verifica che in demo risponda con esito simulato."""
    with patch("src.api.routers.auth.is_demo_mode", return_value=True):
        res = client.post("/api/auth/change-email", json={
            "new_email": "newdemo@example.com"
        })
        assert res.status_code == 200
        assert res.json()["success"] is True


def test_change_email_success(client):
    """Verifica successo della richiesta di cambio email per utente autenticato."""
    dummy_jwt = jwt.encode({"sub": "real-uuid-1", "email": "test@domain.com"}, "secret", algorithm="HS256")
    with patch("src.api.routers.auth.is_demo_mode", return_value=False), \
         patch("src.api.routers.auth.is_local_sqlite", return_value=False), \
         patch("src.api.routers.auth.DEMO_MODE", False), \
         patch("src.services.auth.auth_service.update_user_email", return_value=(True, "Richiesta inviata!")):
        res = client.post(
            "/api/auth/change-email",
            json={"new_email": "updated@domain.com"},
            headers={"Authorization": f"Bearer {dummy_jwt}"}
        )
        assert res.status_code == 200
        assert res.json()["success"] is True


def test_change_password_unauthorized(client):
    """Verifica rifiuto con HTTP 401 per tentativo di cambio password senza credenziali."""
    with patch("src.api.deps.is_demo_mode", return_value=False), \
         patch("src.api.deps.is_local_sqlite", return_value=False), \
         patch("src.api.deps.DEMO_MODE", False):
        res = client.post("/api/auth/change-password", json={
            "current_password": "currentPassword123",
            "new_password": "newPassword123"
        })
        assert res.status_code == 401


def test_change_email_unauthorized(client):
    """Verifica rifiuto con HTTP 401 per tentativo di cambio email senza credenziali."""
    with patch("src.api.deps.is_demo_mode", return_value=False), \
         patch("src.api.deps.is_local_sqlite", return_value=False), \
         patch("src.api.deps.DEMO_MODE", False):
        res = client.post("/api/auth/change-email", json={
            "new_email": "brandnew@example.com"
        })
        assert res.status_code == 401


def test_change_email_identical_error(client):
    """Verifica rifiuto con HTTP 400 se la nuova email coincide con quella attuale."""
    current_mail = "user@domain.com"
    dummy_jwt = jwt.encode({"sub": "real-uuid-1", "email": current_mail}, "secret", algorithm="HS256")
    with patch("src.api.routers.auth.is_demo_mode", return_value=False), \
         patch("src.api.routers.auth.is_local_sqlite", return_value=False), \
         patch("src.api.routers.auth.DEMO_MODE", False):
        res = client.post(
            "/api/auth/change-email",
            json={"new_email": current_mail},
            headers={"Authorization": f"Bearer {dummy_jwt}"}
        )
        assert res.status_code == 400
        assert "coincide con quello attuale" in res.json()["detail"]

