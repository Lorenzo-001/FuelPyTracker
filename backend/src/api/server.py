# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from fastapi.responses import RedirectResponse
import datetime

# Inizializza l'applicazione FastAPI
app = FastAPI(
    title="FuelPyTracker API",
    description="Backend API per FuelPyTracker V2.0",
    version="2.0.0"
)

# Configura CORS per permettere al frontend React di chiamare le API
# (In produzione sostituire * con il dominio di Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

