"""
Configurazione centralizzata del logging per il backend FastAPI.
Filtra gli endpoint ad alto volume (es. /health polling) e silenzia warning legacy di Streamlit.
"""
from __future__ import annotations

import logging
from typing import Sequence

# Fallback opzionale a livello di modulo per silenziamento Streamlit legacy
try:
    import streamlit.runtime.caching.cache_data_api as cda
except Exception:
    cda = None  # type: ignore

try:
    import streamlit.logger as st_logger
except Exception:
    st_logger = None  # type: ignore


class EndpointFilter(logging.Filter):
    """Filtro di logging che esclude richieste verso specifici endpoint ad alto volume (es. /health)."""

    def __init__(self, excluded_endpoints: Sequence[str] = ("/health", "/favicon.ico")) -> None:
        super().__init__()
        self.excluded_endpoints = tuple(excluded_endpoints)

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        if any(endpoint in message for endpoint in self.excluded_endpoints):
            return False
        if record.args:
            args_str = " ".join(str(a) for a in record.args)
            if any(endpoint in args_str for endpoint in self.excluded_endpoints):
                return False
        return True


def configure_api_logging() -> None:
    """Configura filtri e livelli di log per un ambiente console pulito e focalizzato."""
    # 1. Disabilita warning interni di Streamlit quando i moduli DB vengono invocati da FastAPI
    if cda is not None:
        try:
            cda._LOGGER.disabled = True
        except Exception:
            pass

    if st_logger is not None:
        try:
            st_logger.set_log_level("error")
        except Exception:
            pass

    # 2. Applica EndpointFilter al logger access di Uvicorn e ai suoi handler
    endpoint_filter = EndpointFilter(("/health", "/favicon.ico"))
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.addFilter(endpoint_filter)

    for handler in access_logger.handlers:
        handler.addFilter(endpoint_filter)
