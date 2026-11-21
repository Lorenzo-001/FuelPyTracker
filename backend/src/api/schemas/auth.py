"""
Modelli Pydantic per l'autenticazione (contratti dati HTTP).
Definisce le strutture di input e output per le route di login, registrazione e profilo.
"""
from __future__ import annotations

# pyrefly: ignore [missing-import]
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Payload per la richiesta di autenticazione."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password dell'account (min 6 caratteri)")


class RegisterRequest(BaseModel):
    """Payload per la registrazione di un nuovo account."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password scelta (min 6 caratteri)")


class UserResponse(BaseModel):
    """Dati anagrafici e permessi dell'utente restituito all'interfaccia."""
    id: str
    email: str
    is_demo: bool = False


class TokenResponse(BaseModel):
    """Risposta di sessione contenente il token JWT e i dettagli dell'utente."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordResetRequest(BaseModel):
    """Payload per la richiesta di email di recupero password."""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """Payload per il completamento del recupero password via token ricevuto via email."""
    access_token: str = Field(..., min_length=10, description="Token di recupero fornito da Supabase via email")
    refresh_token: str | None = Field(None, description="Refresh token opzionale")
    new_password: str = Field(..., min_length=8, max_length=128, description="Nuova password scelta (min 8 caratteri)")


class PasswordChangeRequest(BaseModel):
    """Payload per la modifica protetta della password da parte dell'utente autenticato."""
    current_password: str = Field(..., min_length=1, description="Password attuale dell'utente per verifica identità")
    new_password: str = Field(..., min_length=8, max_length=128, description="Nuova password desiderata (min 8 caratteri)")


class EmailChangeRequest(BaseModel):
    """Payload per la richiesta di modifica indirizzo email."""
    new_email: EmailStr = Field(..., description="Nuovo indirizzo email desiderato")


class MessageResponse(BaseModel):
    """Risposta generica con messaggio informativo."""
    message: str
    success: bool = True
