"""
Configurazione centralizzata per il server FastAPI.
Carica le variabili d'ambiente da file .env e fornisce costanti tipizzate.
"""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Carica .env cercando prima nella cartella backend, poi nella root
for env_path in [
    Path(__file__).resolve().parent.parent.parent / ".env",
    Path.cwd() / "backend" / ".env",
    Path.cwd() / ".env",
]:
    if env_path.is_file():
        load_dotenv(env_path)
        break

# Informazioni API
API_TITLE = "FuelPyTracker API"
API_DESCRIPTION = "Backend REST API disaccoppiato per FuelPyTracker V2.0"
API_VERSION = "2.0.0"
API_PREFIX = "/api"

# Configurazione CORS
_cors_env = os.environ.get("CORS_ORIGINS", "*")
CORS_ORIGINS = [origin.strip() for origin in _cors_env.split(",") if origin.strip()]

# Flag Demo Mode e utente predefinito
_TRUTHY = ("1", "true", "yes")
DEMO_MODE = os.environ.get("DEMO_MODE", "").strip().lower() in _TRUTHY
DEMO_USER_ID = os.environ.get("DEMO_USER_ID", "00000000-0000-4000-8000-000000000001")
DEMO_USER_EMAIL = os.environ.get("DEMO_USER_EMAIL", "demo@local.fuelpytracker")

# Chiave opzionale per validazione firma JWT (Supabase JWT Secret)
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "").strip() or None
