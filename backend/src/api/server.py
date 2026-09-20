import sys
from pathlib import Path
import datetime
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.responses import RedirectResponse

# Assicura la presenza della cartella backend nel sys.path per importare src.*
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.api.config import API_TITLE, API_DESCRIPTION, API_VERSION, CORS_ORIGINS

# Inizializza l'applicazione FastAPI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

# Configura CORS per consentire chiamate dal frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.routers.auth import router as auth_router

# Registra i router modulari dell'API
app.include_router(auth_router, prefix="/api")



@app.get("/", include_in_schema=False)

def root():
    """Reindirizza alla documentazione Swagger interattiva."""
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["System"])
def health_check():
    """
    Endpoint di health-check.
    Utilizzato da UptimeRobot o altri cron per prevenire il cold start del server.
    """
    return {
        "status": "ok",
        "version": "2.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

