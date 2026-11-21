"""
Test unitari per le dipendenze e l'infrastruttura core di FastAPI (deps.py, config.py, url.py).
"""
import pytest
import jwt
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.api.deps import get_db, get_current_user_id
from src.database.url import resolve_database_url


# =============================================================================
# TEST: get_db dependency
# =============================================================================

def test_get_db_yields_session_and_closes():
    """Verifica che get_db fornisca una sessione e ne garantisca la chiusura."""
    gen = get_db()
    db = next(gen)
    assert isinstance(db, Session)
    
    # Simula termine ciclo di vita richiesta HTTP
    with pytest.raises(StopIteration):
        next(gen)


# =============================================================================
# TEST: get_current_user_id
# =============================================================================

def test_get_current_user_id_with_valid_jwt():
    """Verifica l'estrazione corretta dell'ID utente dal claim 'sub' di un token JWT."""
    test_uid = "user-uuid-12345"
    token = jwt.encode({"sub": test_uid, "email": "test@example.com"}, "secret", algorithm="HS256")
    
    resolved_id = get_current_user_id(authorization=f"Bearer {token}")
    assert resolved_id == test_uid


def test_get_current_user_id_with_invalid_jwt():
    """Verifica che un token JWT malformato sollevi 401 Unauthorized."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_id(authorization="Bearer token_non_valido_xyz")
    assert exc_info.value.status_code == 401


def test_get_current_user_id_with_x_user_id_header():
    """Verifica che l'header X-User-Id venga utilizzato correttamente."""
    custom_uid = "custom-dev-user-999"
    resolved_id = get_current_user_id(x_user_id=custom_uid)
    assert resolved_id == custom_uid


def test_get_current_user_id_demo_fallback():
    """Verifica il fallback trasparente su DEMO_USER_ID quando la modalità demo è attiva."""
    with patch("src.api.deps.is_demo_mode", return_value=True):
        uid = get_current_user_id()
        assert uid is not None
        assert len(uid) > 0


def test_get_current_user_id_unauthorized_in_prod():
    """Verifica che in assenza di credenziali e fuori da demo/sqlite venga sollevato 401."""
    with patch("src.api.deps.is_demo_mode", return_value=False), \
         patch("src.api.deps.is_local_sqlite", return_value=False), \
         patch("src.api.deps.DEMO_MODE", False):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id(authorization=None, x_user_id=None)
        assert exc_info.value.status_code == 401


# =============================================================================
# TEST: resolve_database_url
# =============================================================================

def test_resolve_database_url_from_env():
    """Verifica la priorità della variabile d'ambiente DATABASE_URL."""
    fake_url = "postgresql://user:pass@host:5432/db"
    with patch.dict("os.environ", {"DATABASE_URL": fake_url}):
        assert resolve_database_url() == fake_url


def test_resolve_database_url_normalizes_postgres_prefix():
    """Verifica che postgres:// venga automaticamente convertito in postgresql://."""
    legacy_url = "postgres://user:pass@host:5432/db"
    with patch.dict("os.environ", {"DATABASE_URL": legacy_url}):
        assert resolve_database_url() == "postgresql://user:pass@host:5432/db"


def test_resolve_database_url_sqlite():
    """Verifica la risoluzione dell'URL SQLite quando LOCAL_SQLITE=True."""
    with patch.dict("os.environ", {"DATABASE_URL": "", "LOCAL_SQLITE": "True"}):
        url = resolve_database_url()
        assert url.startswith("sqlite:///")
        assert "local.db" in url
