"""
Router API per l'Autenticazione e la gestione Utenti (/api/auth).
Gestisce flussi di Login, Registrazione, Profilo Utente e Recupero Password.
Supporta sia l'integrazione con Supabase Auth che la modalità Demo locale.
"""
from __future__ import annotations

import logging
import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, status

from src.api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    PasswordChangeRequest,
    EmailChangeRequest,
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
    description="Invia un'email contenente il link sicuro per la reimpostazione della password.",
)
def reset_password(payload: PasswordResetRequest) -> MessageResponse:
    # 1. Sandbox / Demo Mode
    if is_demo_mode() or is_local_sqlite() or DEMO_MODE:
        return MessageResponse(
            message="Se l'indirizzo email è associato a un account, riceverai a breve le istruzioni di recupero.",
            success=True,
        )

    # 2. Richiesta a Supabase Auth
    # Principio di sicurezza OWASP Anti-Enumeration:
    # Restituiamo sempre un messaggio neutro di conferma per evitare che un attaccante
    # possa scoprire se un'email è registrata o meno nel sistema.
    ok, err_msg = auth_service.send_password_reset_email(str(payload.email))
    if not ok:
        logger.info("Reset password non inviato per '%s': %s", payload.email, err_msg)

    return MessageResponse(
        message="Se l'indirizzo email è associato a un account, riceverai a breve le istruzioni di recupero.",
        success=True,
    )


@router.post(
    "/update-password-recovery",
    response_model=MessageResponse,
    summary="Imposta una nuova password utilizzando il token di recupero",
    description="Permette di impostare una nuova credenziale dopo aver verificato il link ricevuto via email.",
)
def update_password_recovery(payload: PasswordResetConfirmRequest) -> MessageResponse:
    if is_demo_mode() or is_local_sqlite() or DEMO_MODE:
        return MessageResponse(
            message="Password aggiornata con successo in ambiente Demo!",
            success=True,
        )

    ok, msg = auth_service.update_password_with_recovery_token(
        access_token=payload.access_token,
        new_password=payload.new_password,
        refresh_token=payload.refresh_token,
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )

    return MessageResponse(
        message="Password aggiornata con successo! Ora puoi effettuare l'accesso con le nuove credenziali.",
        success=True,
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Modifica la password dell'utente autenticato",
    description="Richiede la verifica della password attuale prima di impostare la nuova password.",
)
def change_password(
    payload: PasswordChangeRequest,
    user_id: str = Depends(get_current_user_id),
    authorization: str | None = Header(None, alias="Authorization"),
) -> MessageResponse:
    # 1. Sicurezza: validazione che la nuova password sia diversa dalla vecchia
    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nuova password deve essere diversa da quella attuale.",
        )

    # 2. In Sandbox / Demo Mode
    if user_id == DEMO_USER_ID or is_demo_mode() or is_local_sqlite() or DEMO_MODE:
        return MessageResponse(
            message="Password modificata con successo in ambiente Demo!",
            success=True,
        )

    # 3. Risoluzione email dell'utente autenticato
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    email = None
    if token:
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            email = decoded.get("email")
        except Exception:
            pass

    if not email:
        client = auth_service.get_client()
        if client and token:
            try:
                user_info = client.auth.get_user(jwt=token)
                if user_info and user_info.user and user_info.user.email:
                    email = user_info.user.email
            except Exception:
                pass

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossibile identificare l'email associata alla sessione attiva.",
        )

    # 4. Verifica password attuale e aggiornamento protetto tramite auth_service
    ok, msg = auth_service.update_user_password_secure(
        email=email,
        old_password=payload.current_password,
        new_password=payload.new_password,
    )

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )

    return MessageResponse(
        message=msg,
        success=True,
    )


@router.post(
    "/change-email",
    response_model=MessageResponse,
    summary="Richiede la modifica dell'indirizzo email dell'account",
    description="Avvia la procedura di verifica email con conferma a doppio indirizzo tramite Supabase.",
)
def change_email(
    payload: EmailChangeRequest,
    user_id: str = Depends(get_current_user_id),
    authorization: str | None = Header(None, alias="Authorization"),
) -> MessageResponse:
    # 1. In Sandbox / Demo Mode
    if user_id == DEMO_USER_ID or is_demo_mode() or is_local_sqlite() or DEMO_MODE:
        return MessageResponse(
            message="Richiesta di cambio email simulata in ambiente Demo.",
            success=True,
        )

    # 2. Estrazione token Bearer
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessione di autenticazione non valida.",
        )

    # Verifica di sicurezza: il nuovo indirizzo deve essere diverso da quello attuale
    current_email = None
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        current_email = decoded.get("email")
    except Exception:
        pass

    if current_email and str(payload.new_email).strip().lower() == current_email.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il nuovo indirizzo email coincide con quello attuale.",
        )

    # 3. Invio richiesta di aggiornamento a Supabase
    ok, msg = auth_service.update_user_email(
        new_email=str(payload.new_email),
        user_token=token,
    )

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
        )

    return MessageResponse(
        message=msg,
        success=True,
    )
