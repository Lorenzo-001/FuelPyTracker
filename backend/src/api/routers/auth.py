"""
Router API per l'Autenticazione e la gestione Utenti (/api/auth).
Gestisce flussi di Login, Registrazione, Profilo Utente e Recupero Password.
Supporta sia l'integrazione con Supabase Auth che la modalità Demo locale.
"""
from __future__ import annotations

import logging
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
    TokenResponse,
    PasswordResetRequest,
    MessageResponse,
)
from src.api.deps import get_current_user_id
from src.api.config import DEMO_MODE, DEMO_USER_ID, DEMO_USER_EMAIL
from src.demo import is_demo_mode
from src.database.url import is_local_sqlite
from src.services.auth import auth_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Esegue il login utente",
    description="Autentica l'utente tramite email e password. Restituisce il token JWT per le chiamate successive.",
)
def login(payload: LoginRequest) -> TokenResponse:
    # 1. Gestione Sandbox / Demo Mode
    if is_demo_mode() or is_local_sqlite() or DEMO_MODE or payload.email == DEMO_USER_EMAIL:
        return TokenResponse(
            access_token="demo-session-token",
            token_type="bearer",
            user=UserResponse(
                id=DEMO_USER_ID,
                email=str(payload.email),
                is_demo=True,
            ),
        )

    # 2. Autenticazione tramite Supabase Auth
    try:
        res = auth_service.sign_in(str(payload.email), payload.password)
        if not res or not res.session or not res.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenziali non valide o utente non trovato.",
            )

        return TokenResponse(
            access_token=res.session.access_token,
            token_type="bearer",
            user=UserResponse(
                id=str(res.user.id),
                email=str(res.user.email),
                is_demo=False,
            ),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Tentativo di login fallito per %s: %s", payload.email, exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenziali errate o account non confermato.",
        ) from exc


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra un nuovo account",
)
def register(payload: RegisterRequest) -> MessageResponse:
    # In demo mode la registrazione è simulata
    if is_demo_mode() or is_local_sqlite() or DEMO_MODE:
        return MessageResponse(
            message="Registrazione simulata completata in ambiente Demo.",
            success=True,
        )

    try:
        auth_service.sign_up(str(payload.email), payload.password)
        return MessageResponse(
            message="Registrazione completata! Controlla la tua posta per confermare l'account.",
            success=True,
        )
    except Exception as exc:
        logger.error("Errore durante la registrazione di %s: %s", payload.email, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossibile completare la registrazione: {exc}",
        ) from exc


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Effettua il logout",
)
def logout() -> MessageResponse:
    try:
        auth_service.sign_out()
    except Exception:
        pass  # In ambiente stateless, il client rimuove semplicemente il token
    return MessageResponse(message="Logout effettuato con successo.", success=True)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Recupera il profilo dell'utente autenticato",
)
def get_me(user_id: str = Depends(get_current_user_id)) -> UserResponse:
    # Se utente demo identificato da deps
    if user_id == DEMO_USER_ID:
        return UserResponse(
            id=DEMO_USER_ID,
            email=DEMO_USER_EMAIL,
            is_demo=True,
        )

    # Utente reale autenticato da token
    client = auth_service.get_client()
    email = "utente@fuelpytracker.com"
    if client:
        try:
            user_data = client.auth.get_user()
            if user_data and user_data.user and user_data.user.email:
                email = str(user_data.user.email)
        except Exception:
            pass

    return UserResponse(
        id=user_id,
        email=email,
        is_demo=False,
    )



@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Richiede l'invio dell'email di recupero password",
)
def reset_password(payload: PasswordResetRequest) -> MessageResponse:
    if is_demo_mode() or is_local_sqlite() or DEMO_MODE:
        return MessageResponse(
            message="Invio email simulato in ambiente Demo.",
            success=True,
        )

    ok, msg = auth_service.send_password_reset_email(str(payload.email))
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )
    return MessageResponse(message=msg, success=True)
