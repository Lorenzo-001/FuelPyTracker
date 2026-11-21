"""
Dipendenze riutilizzabili per FastAPI (Dependency Injection).
Gestisce la sessione database e l'estrazione sicura dell'utente autenticato.
"""
from __future__ import annotations

import logging
from typing import Generator
# pyrefly: ignore [missing-import]
import jwt
# pyrefly: ignore [missing-import]
from fastapi import Header, HTTPException, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from src.database.core import SessionLocal
from src.database.url import is_local_sqlite
from src.demo import is_demo_mode
from src.api.config import DEMO_MODE, DEMO_USER_ID, SUPABASE_JWT_SECRET
from src.services.auth import auth_service

logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    Fornisce una sessione database isolata per ciascuna richiesta HTTP.
    Garantisce la chiusura della connessione nel blocco finally.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(
    authorization: str | None = Header(None, alias="Authorization"),
    x_user_id: str | None = Header(None, alias="X-User-Id"),
) -> str:
    """
    Estrae e valida l'ID utente dalla richiesta:
    1. Se presente un Bearer token (JWT Supabase), ne estrae il claim 'sub'.
    2. Se presente l'header 'X-User-Id' (dev/testing), ne restituisce il valore.
    3. Se in modalità Demo o SQLite locale, effettua il fallback sull'utente demo.
    4. Negli altri casi solleva un errore 401 Unauthorized.
    """
    # Gestisce sia l'iniezione FastAPI (str) sia la chiamata diretta nei test (Header object o None)
    auth_val = authorization if isinstance(authorization, str) else None
    uid_val = x_user_id if isinstance(x_user_id, str) else None

    # 1. Verifica token Bearer (Supabase JWT o token Demo)
    if auth_val and auth_val.lower().startswith("bearer "):
        token = auth_val.split(" ", 1)[1].strip()
        if token == "demo-session-token" and (is_demo_mode() or is_local_sqlite() or DEMO_MODE):
            return DEMO_USER_ID

        try:
            if SUPABASE_JWT_SECRET:
                payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
            else:
                # Decodifica payload JWT senza verifica firma (gestita a monte da Supabase)
                payload = jwt.decode(token, options={"verify_signature": False})
            
            user_id = payload.get("sub")
            if user_id:
                return str(user_id)
        except Exception as exc:
            logger.warning("Token JWT non valido: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token di autenticazione non valido o scaduto.",
            ) from exc

    # 2. Header custom per test e ambienti di sviluppo
    if uid_val and uid_val.strip():
        return uid_val.strip()

    # 3. Fallback trasparente su utente demo (locale, sandbox o sqlite)
    if is_demo_mode() or is_local_sqlite() or DEMO_MODE:
        return DEMO_USER_ID


    # 4. Accesso negato se nessun metodo di autenticazione è soddisfatto
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Autenticazione richiesta. Fornire un token Bearer valido.",
    )
