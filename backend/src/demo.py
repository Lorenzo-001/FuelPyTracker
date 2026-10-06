"""
src/demo.py — Feature Flag per la modalità Sandbox/Demo

Espone:
  - is_demo_mode() -> bool      : utente fittizio / mock OCR / skip auth cloud
  - writes_disabled() -> bool  : sola lettura UI (demo cloud; False con LOCAL_SQLITE)
  - DEMO_USER                  : SimpleNamespace compatibile con le funzioni CRUD
  - mock_analyze_receipt()     : Risposta OCR simulata (senza chiamate a OpenAI)

Lettura del flag (priorità decrescente):
  1. Variabile d'ambiente OS  (sviluppo locale, .env, CI, Docker)
  2. Se DEMO_MODE assente e LOCAL_SQLITE=True → demo on (bootstrap zero-cloud)

Variabili richieste quando DEMO_MODE=True:
  DEMO_USER_ID     — UUID Supabase dell'utente demo
  DEMO_USER_EMAIL  — Email dell'utente demo
"""
from __future__ import annotations

import os
import time
from datetime import date
from types import SimpleNamespace

from src.database.url import is_local_sqlite


# =============================================================================
# FLAG HELPER
# =============================================================================

def is_demo_mode() -> bool:
    """
    Restituisce True se la modalità demo è attiva.
    Priorità:
      1. Variabile OS DEMO_MODE (se presente in os.environ, è definitiva)
      2. LOCAL_SQLITE senza DEMO_MODE in env → True (bootstrap locale)
    """
    if "DEMO_MODE" in os.environ:
        return os.environ["DEMO_MODE"].strip().lower() in ("1", "true", "yes")

    if is_local_sqlite():
        return True

    return False


def writes_disabled() -> bool:
    """True solo in demo pubblica cloud: locale SQLite resta scrivibile."""
    return is_demo_mode() and not is_local_sqlite()


def _get_demo_credential(env_key: str) -> str | None:
    """Legge una credenziale demo dall'ambiente OS."""
    val = os.environ.get(env_key, "").strip()
    return val or None


# =============================================================================
# DEMO USER
# =============================================================================

def _build_demo_user() -> SimpleNamespace:
    """
    Costruisce il SimpleNamespace DEMO_USER leggendo le credenziali dall'ambiente.
    Solleva ValueError se le variabili obbligatorie mancano in modalità demo.
    """
    user_id = _get_demo_credential("DEMO_USER_ID")
    user_email = _get_demo_credential("DEMO_USER_EMAIL")

    if not user_id or not user_email:
        raise ValueError(
            "[DEMO_MODE] Variabili DEMO_USER_ID e/o DEMO_USER_EMAIL non configurate. "
            "Aggiungile al file .env (sviluppo) prima di avviare l'applicazione in modalità Demo."
        )

    return SimpleNamespace(id=user_id, email=user_email)


class _LazyDemoUser:
    """Wrapper lazy per DEMO_USER: costruisce il SimpleNamespace al primo accesso."""

    def __init__(self):
        self._user: SimpleNamespace | None = None

    def _resolve(self) -> SimpleNamespace:
        if self._user is None:
            self._user = _build_demo_user()
        return self._user

    def __getattr__(self, name: str):
        return getattr(self._resolve(), name)

    def __repr__(self) -> str:
        return repr(self._resolve())


DEMO_USER = _LazyDemoUser()


# =============================================================================
# MOCK OCR
# =============================================================================

def mock_analyze_receipt():
    """
    Simula un'analisi OCR restituendo dati plausibili senza chiamare OpenAI.
    Il sleep simula la latenza della chiamata AI per un'esperienza realistica.

    Returns:
        ReceiptData: DTO con dati di rifornimento fittizi ma coerenti.
    """
    from src.services.ocr.models import ReceiptData  # Lazy import per prevenire import circolare

    time.sleep(2)

    rd = ReceiptData()
    rd.raw_text = "✅ [DEMO] Analisi simulata — nessuna chiamata API effettuata."
    rd.total_cost = 68.50
    rd.price_per_liter = 1.869
    rd.liters = round(rd.total_cost / rd.price_per_liter, 2)
    rd.station_name = "Eni Station Demo"
    rd.date = date.today()
    return rd
