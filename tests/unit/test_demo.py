"""
tests/unit/test_demo.py — Unit test per il modulo src/demo.py

Copre:
  1. is_demo_mode() → True  quando DEMO_MODE=True è nell'env
  2. is_demo_mode() → False quando la variabile è assente o falsy
  3. DEMO_USER risolve correttamente id e email dalle env vars
  4. DEMO_USER solleva ValueError se le credenziali mancano in DEMO_MODE=True
  5. mock_analyze_receipt() restituisce un ReceiptData valido con campi coerenti
"""
import pytest
import os
from datetime import date
from unittest.mock import patch


# ---------------------------------------------------------------------------
# is_demo_mode()
# ---------------------------------------------------------------------------

class TestIsDemoMode:

    def test_returns_true_when_env_is_true(self):
        with patch.dict("os.environ", {"DEMO_MODE": "True"}):
            from src.demo import is_demo_mode
            assert is_demo_mode() is True

    def test_returns_true_when_env_is_1(self):
        with patch.dict("os.environ", {"DEMO_MODE": "1"}):
            from src.demo import is_demo_mode
            assert is_demo_mode() is True

    def test_returns_false_when_env_is_false(self):
        with patch.dict("os.environ", {"DEMO_MODE": "False"}):
            from src.demo import is_demo_mode
            assert is_demo_mode() is False

    def test_returns_false_when_env_is_absent(self):
        # Sovrascriviamo con stringa vuota per simulare variabile non configurata.
        # Non usiamo clear=True perché DEMO_MODE potrebbe essere già in os.environ
        # (es. caricato dal processo genitore di pytest).
        with patch.dict("os.environ", {"DEMO_MODE": ""}):
            from src.demo import is_demo_mode
            assert is_demo_mode() is False



# ---------------------------------------------------------------------------
# DEMO_USER  (ora dinamico — caricato dalle env vars)
# ---------------------------------------------------------------------------

_FAKE_ID    = "aaaabbbb-cccc-dddd-eeee-ffffeeeebbbb"
_FAKE_EMAIL = "test-demo@fuelpytracker.com"

class TestDemoUser:

    def test_demo_user_has_correct_id(self):
        """DEMO_USER.id viene letto da DEMO_USER_ID nell'env."""
        with patch.dict("os.environ", {"DEMO_USER_ID": _FAKE_ID,
                                       "DEMO_USER_EMAIL": _FAKE_EMAIL}):
            import importlib, src.demo as dm
            # Forziamo la ricostruzione del lazy wrapper
            dm.DEMO_USER._user = None
            assert dm.DEMO_USER.id == _FAKE_ID

    def test_demo_user_has_correct_email(self):
        """DEMO_USER.email viene letto da DEMO_USER_EMAIL nell'env."""
        with patch.dict("os.environ", {"DEMO_USER_ID": _FAKE_ID,
                                       "DEMO_USER_EMAIL": _FAKE_EMAIL}):
            import src.demo as dm
            dm.DEMO_USER._user = None
            assert dm.DEMO_USER.email == _FAKE_EMAIL

    def test_demo_user_raises_if_credentials_missing(self):
        """Se DEMO_USER_ID/DEMO_USER_EMAIL sono vuoti E st.secrets non ha valori demo,
        _build_demo_user solleva ValueError."""
        # 1. Env vars vuote (mascherano valori da .env già caricato nel processo)
        # 2. Mock di st.secrets per bloccare il fallback su secrets.toml
        mock_secrets = {"demo": {}}
        with patch.dict("os.environ", {"DEMO_USER_ID": "", "DEMO_USER_EMAIL": ""}), \
             patch("src.demo.is_demo_mode", return_value=False):
            # Importiamo qui per evitare cache del modulo
            import importlib, src.demo as dm
            # Rimpiazziamo il singolo lookup st.secrets con una versione che restituisce {}
            original_get = dm._get_demo_credential
            def _empty_cred(env_key, secrets_key):
                return None
            dm._get_demo_credential = _empty_cred
            try:
                with pytest.raises(ValueError, match="DEMO_USER_ID"):
                    dm._build_demo_user()
            finally:
                dm._get_demo_credential = original_get



# ---------------------------------------------------------------------------
# mock_analyze_receipt()
# ---------------------------------------------------------------------------

class TestMockAnalyzeReceipt:

    def test_returns_receipt_data_instance(self):
        from src.demo import mock_analyze_receipt
        from src.services.ocr.models import ReceiptData
        with patch("src.demo.time.sleep"):
            result = mock_analyze_receipt()
        assert isinstance(result, ReceiptData)

    def test_receipt_data_has_nonzero_cost(self):
        from src.demo import mock_analyze_receipt
        with patch("src.demo.time.sleep"):
            result = mock_analyze_receipt()
        assert result.total_cost > 0

    def test_receipt_data_has_nonzero_liters(self):
        from src.demo import mock_analyze_receipt
        with patch("src.demo.time.sleep"):
            result = mock_analyze_receipt()
        assert result.liters > 0

    def test_receipt_data_has_station_name(self):
        from src.demo import mock_analyze_receipt
        with patch("src.demo.time.sleep"):
            result = mock_analyze_receipt()
        assert result.station_name is not None and result.station_name != ""

    def test_receipt_data_date_is_today(self):
        from src.demo import mock_analyze_receipt
        with patch("src.demo.time.sleep"):
            result = mock_analyze_receipt()
        assert result.date == date.today()

    def test_liters_is_consistent_with_cost_and_price(self):
        from src.demo import mock_analyze_receipt
        with patch("src.demo.time.sleep"):
            result = mock_analyze_receipt()
        expected_liters = round(result.total_cost / result.price_per_liter, 2)
        assert result.liters == expected_liters
