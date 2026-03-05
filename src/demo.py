"""
src/demo.py — Feature Flag per la modalità Sandbox/Demo

Espone:
  - is_demo_mode() -> bool  : True se DEMO_MODE è attivo
  - DEMO_USER               : SimpleNamespace compatibile con le funzioni CRUD
  - mock_analyze_receipt()  : Risposta OCR simulata (senza chiamate a OpenAI)

Lettura del flag (priorità decrescente):
  1. Variabile d'ambiente OS  (sviluppo locale, .env)
  2. Streamlit Secrets        (Streamlit Cloud / deploy)

Variabili richieste quando DEMO_MODE=True:
  DEMO_USER_ID     — UUID Supabase dell'utente demo
  DEMO_USER_EMAIL  — Email dell'utente demo
"""
from __future__ import annotations

import os
import time
from datetime import date
from types import SimpleNamespace


# =============================================================================
# FLAG HELPER
# =============================================================================

def is_demo_mode() -> bool:
    """
    Restituisce True se la modalità demo è attiva.
    Priorità:
      1. Variabile OS DEMO_MODE (se presente in os.environ, è definitiva — no fallback)
      2. st.secrets [demo] enabled (solo se DEMO_MODE non è nell'env)
    """
    # 1. Variabile d'ambiente (locale + Docker + CI)
    # Nota: controlliamo la presenza PRIMA del valore, così un override esplicito
    # (es. DEMO_MODE="" nei test) non cade nel fallback st.secrets.
    if "DEMO_MODE" in os.environ:
        return os.environ["DEMO_MODE"].strip().lower() in ("1", "true", "yes")

    # 2. Streamlit Secrets (Streamlit Cloud) — solo se env var non è settata
    try:
        import streamlit as st
        return bool(st.secrets.get("demo", {}).get("enabled", False))
    except Exception:
        return False


def _get_demo_credential(env_key: str, secrets_key: str) -> str | None:
    """
    Legge una credenziale demo prima dall'env OS, poi da st.secrets.
    Restituisce None se non trovata in nessuna sorgente.
    """
    val = os.environ.get(env_key, "").strip()
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get("demo", {}).get(secrets_key) or None
    except Exception:
        return None


# =============================================================================
# DEMO USER
# =============================================================================
# I valori vengono risolti a runtime; le credenziali NON sono nel codice sorgente.
# Configurare le variabili seguenti (env o st.secrets):
#   DEMO_USER_ID     / [demo] user_id
#   DEMO_USER_EMAIL  / [demo] user_email
# Se DEMO_MODE=True e queste variabili mancano, l'app solleva ValueError
# al primo accesso a DEMO_USER, evitando avvii silenziosi con dati corrotti.
# =============================================================================

def _build_demo_user() -> SimpleNamespace:
    """
    Costruisce il SimpleNamespace DEMO_USER leggendo le credenziali dall'ambiente.
    Solleva ValueError se le variabili obbligatorie mancano in modalità demo.
    """
    user_id    = _get_demo_credential("DEMO_USER_ID",    "user_id")
    user_email = _get_demo_credential("DEMO_USER_EMAIL", "user_email")

    if not user_id or not user_email:
        raise ValueError(
            "[DEMO_MODE] Variabili DEMO_USER_ID e/o DEMO_USER_EMAIL non configurate. "
            "Aggiungile al file .env (sviluppo) o ai Streamlit Secrets (deploy) prima "
            "di avviare l'applicazione in modalità Demo."
        )

    return SimpleNamespace(id=user_id, email=user_email)


# Proprietà lazy: l'oggetto viene costruito solo quando viene effettivamente usato,
# permettendo all'app di avviarsi normalmente anche senza le variabili (DEMO_MODE=False).
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
    from src.services.ocr.models import ReceiptData  # import locale per evitare circoli

    time.sleep(2)  # Latenza verosimile (≈ GPT-4o Vision)

    rd = ReceiptData()
    rd.raw_text        = "✅ [DEMO] Analisi simulata — nessuna chiamata API effettuata."
    rd.total_cost      = 68.50
    rd.price_per_liter = 1.869
    rd.liters          = round(rd.total_cost / rd.price_per_liter, 2)  # ≈ 36.65
    rd.station_name    = "Eni Station Demo"
    rd.date            = date.today()
    return rd
