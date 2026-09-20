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


class MessageResponse(BaseModel):
    """Risposta generica con messaggio informativo."""
    message: str
    success: bool = True
