# =============================================================================
# FuelPyTracker V2 — Backend Production Dockerfile (FastAPI + Uvicorn)
# =============================================================================

FROM python:3.11-slim

# 1. Impostazioni ambiente Python per produzione
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PORT=8000

WORKDIR /app

# 2. Installa curl per l'Healthcheck e ripulisci la cache apt
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Dipendenze Python (sfruttando la cache layer di Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 4. Copia del codice applicativo
COPY . .

# 5. Creazione utente di sistema non-root per sicurezza e cartella data persistente
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appgroup /app

USER appuser

# 6. Esposizione porta API REST
EXPOSE 8000

# 7. Healthcheck nativo su GET /health
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# 8. Avvio server di produzione Uvicorn
CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]