"""
Test esteso per OCR engine: errori API, JSON malformato, immagine non leggibile,
client assente, _map_json_to_model con campi parziali.

Questi test completano test_ai_engine.py che copre solo lo happy path.

Esecuzione: pytest tests/unit/ocr/test_ai_engine_errors.py -v
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from openai import AuthenticationError, RateLimitError, APIConnectionError, APIError
from src.services.ocr import engine
from src.services.ocr.models import ReceiptData


# =============================================================================
# HELPERS
# =============================================================================

def _fake_file():
    f = MagicMock()
    f.read.return_value = b"fake_image_bytes"
    f.seek.return_value = None
    return f

def _auth_error():
    """Costruisce AuthenticationError compatibile con openai v1."""
    resp = MagicMock()
    resp.status_code = 401
    resp.headers = {}
    resp.request = MagicMock()
    return AuthenticationError(message="Invalid API key", response=resp, body={})

def _rate_limit_error():
    resp = MagicMock()
    resp.status_code = 429
    resp.headers = {}
    resp.request = MagicMock()
    return RateLimitError(message="Rate limit exceeded", response=resp, body={})

def _api_error():
    resp = MagicMock()
    resp.status_code = 500
    resp.headers = {}
    resp.request = MagicMock()
    return APIError(message="Internal error", request=MagicMock(), body={})


# =============================================================================
# TEST: Client Non Configurato
# =============================================================================

class TestClientNotConfigured:

    def test_no_client_returns_error_receipt_data(self):
        """Se il client OpenAI è None (API key assente), deve tornare ReceiptData con errore."""
        original_client = engine.client
        engine.client = None
        try:
            result = engine.analyze_receipt(_fake_file())
            assert isinstance(result, ReceiptData)
            # total_cost default è 0.0 (non None) nel dataclass
            assert result.total_cost == 0.0
            assert "API Key" in result.raw_text or "mancante" in result.raw_text.lower()
        finally:
            engine.client = original_client


# =============================================================================
# TEST: Errori API OpenAI
# =============================================================================

class TestApiErrors:

    @patch("src.services.ocr.engine.client")
    def test_authentication_error(self, mock_client):
        """API key non valida → ReceiptData con messaggio AUTH."""
        mock_client.chat.completions.create.side_effect = _auth_error()
        result = engine.analyze_receipt(_fake_file())
        assert isinstance(result, ReceiptData)
        assert result.total_cost == 0.0
        assert "AUTH" in result.raw_text or "API Key" in result.raw_text

    @patch("src.services.ocr.engine.client")
    def test_rate_limit_error(self, mock_client):
        """Quota esaurita → ReceiptData con messaggio QUOTA."""
        mock_client.chat.completions.create.side_effect = _rate_limit_error()
        result = engine.analyze_receipt(_fake_file())
        assert isinstance(result, ReceiptData)
        assert result.total_cost == 0.0
        assert "QUOTA" in result.raw_text or "credito" in result.raw_text.lower()

    @patch("src.services.ocr.engine.client")
    def test_connection_error(self, mock_client):
        """Nessuna connessione → ReceiptData con messaggio RETE."""
        mock_client.chat.completions.create.side_effect = APIConnectionError(
            request=MagicMock()
        )
        result = engine.analyze_receipt(_fake_file())
        assert isinstance(result, ReceiptData)
        assert result.total_cost == 0.0
        assert "RETE" in result.raw_text or "connettere" in result.raw_text.lower()

    @patch("src.services.ocr.engine.client")
    def test_api_error_generic(self, mock_client):
        """Errore interno OpenAI → ReceiptData con messaggio SERVER."""
        mock_client.chat.completions.create.side_effect = _api_error()
        result = engine.analyze_receipt(_fake_file())
        assert isinstance(result, ReceiptData)
        assert "SERVER" in result.raw_text or "OpenAI" in result.raw_text

    @patch("src.services.ocr.engine.client")
    def test_json_decode_error(self, mock_client):
        """AI risponde con testo non-JSON → ReceiptData con messaggio AI."""
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Mi dispiace, non riesco ad analizzare."
        mock_client.chat.completions.create.return_value = mock_completion
        result = engine.analyze_receipt(_fake_file())
        assert isinstance(result, ReceiptData)
        assert result.total_cost == 0.0
        assert "AI" in result.raw_text or "formato" in result.raw_text.lower()

    @patch("src.services.ocr.engine.client")
    def test_unexpected_exception(self, mock_client):
        """Qualsiasi altra eccezione non prevista → ReceiptData con errore generico."""
        mock_client.chat.completions.create.side_effect = RuntimeError("Errore imprevisto")
        result = engine.analyze_receipt(_fake_file())
        assert isinstance(result, ReceiptData)
        assert "IMPREVISTO" in result.raw_text or "Errore" in result.raw_text

    @patch("src.services.ocr.engine.client")
    def test_markdown_wrapped_json_still_parsed(self, mock_client):
        """AI a volte risponde con ```json ... ``` — deve essere pulito e parsato."""
        wrapped = '```json\n{"total_cost": 55.0, "price_per_liter": 1.85, "date": null, "station_name": null}\n```'
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = wrapped
        mock_client.chat.completions.create.return_value = mock_completion
        result = engine.analyze_receipt(_fake_file())
        assert isinstance(result, ReceiptData)
        assert result.total_cost == pytest.approx(55.0)


# =============================================================================
# TEST: _map_json_to_model — Campi parziali e date malformate
# =============================================================================

class TestMapJsonToModel:

    def test_all_fields_present(self):
        data = {"total_cost": 80.0, "price_per_liter": 1.80,
                "date": "2024-03-15", "station_name": "ENI"}
        result = engine._map_json_to_model(data)
        assert result.total_cost == 80.0
        assert result.price_per_liter == 1.80
        assert result.station_name == "ENI"
        assert result.liters == pytest.approx(80.0 / 1.80, rel=1e-2)

    def test_partial_fields_no_crash(self):
        """price_per_liter assente (None) → litri non calcolabili, nessun crash."""
        data = {"total_cost": 80.0, "price_per_liter": None,
                "date": None, "station_name": None}
        result = engine._map_json_to_model(data)
        assert result.total_cost == 80.0
        # Senza price_per_liter non si calcolano i litri
        assert result.liters == 0.0

    def test_invalid_date_format_ignored(self):
        """Data in formato errato (non ISO) → il campo date rimane None senza crash."""
        data = {"total_cost": 50.0, "price_per_liter": 1.75,
                "date": "15/03/2024",   # formato non ISO → ignorato
                "station_name": "Q8"}
        result = engine._map_json_to_model(data)
        assert result.date is None
        assert result.total_cost == 50.0

    def test_liters_calculated_from_cost_and_price(self):
        data = {"total_cost": 100.0, "price_per_liter": 2.0,
                "date": None, "station_name": None}
        result = engine._map_json_to_model(data)
        assert result.liters == pytest.approx(50.0)

    def test_empty_dict_returns_default_receipt_data(self):
        """Dizionario vuoto → ReceiptData con tutti i campi al valore default (0.0 / None)."""
        result = engine._map_json_to_model({})
        assert result.total_cost == 0.0
        assert result.price_per_liter == 0.0

    def test_raw_text_is_success_message(self):
        data = {"total_cost": 60.0, "price_per_liter": 1.75,
                "date": "2024-01-15", "station_name": "Agip"}
        result = engine._map_json_to_model(data)
        assert "Completata" in result.raw_text or "GPT" in result.raw_text
