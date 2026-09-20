"""
Tests per il sistema di importazione dati Excel/CSV.
Copertura: utils, fuel importer, maintenance importer, manager.

Esecuzione: pytest tests/unit/importers/test_importers.py -v
"""

import pytest
import pandas as pd
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.services.data.importers.utils import clean_column_names, parse_date, parse_float, parse_int
from src.services.data.importers import fuel as fuel_importer
from src.services.data.importers import maintenance as maint_importer
from src.services.data.importers import manager
from src.database.models import Refueling, Maintenance, AppSettings


# =============================================================================
# FIXTURE COMUNI
# =============================================================================

USER_ID = "test-user-uuid-1234"

def _make_settings(max_cost=200.0):
    """Crea un oggetto AppSettings mock."""
    s = MagicMock(spec=AppSettings)
    s.max_total_cost = max_cost
    s.price_fluctuation_cents = 0.15
    s.import_kml_min   = 3.0
    s.import_kml_max   = 50.0
    s.import_kml_error = 150.0
    s.import_kmd_max   = 1500.0
    return s

def _make_refueling(r_id, d, km, cost=50.0, price=1.75, is_full=True, notes=""):
    r = MagicMock(spec=Refueling)
    r.id = r_id
    r.date = d
    r.total_km = km
    r.total_cost = cost
    r.price_per_liter = price
    r.is_full_tank = is_full
    r.notes = notes
    r.liters = round(cost / price, 2)
    return r

def _make_maintenance(m_id, d, km, expense_type="Tagliando", cost=300.0, description=""):
    m = MagicMock(spec=Maintenance)
    m.id = m_id
    m.date = d
    m.total_km = km
    m.expense_type = expense_type
    m.cost = cost
    m.description = description
    return m


# =============================================================================
# TESTS: utils.py
# =============================================================================

class TestCleanColumnNames:
    def test_lowercase_conversion(self):
        df = pd.DataFrame(columns=["Data", "KM", "PREZZO"])
        result = clean_column_names(df)
        assert list(result.columns) == ["data", "km", "prezzo"]

    def test_strip_whitespace(self):
        df = pd.DataFrame(columns=["  data ", " km ", "prezzo  "])
        result = clean_column_names(df)
        assert list(result.columns) == ["data", "km", "prezzo"]

    def test_mixed_case_and_spaces(self):
        df = pd.DataFrame(columns=["  Data ", "Km Totali", "COSTO TOTALE"])
        result = clean_column_names(df)
        assert list(result.columns) == ["data", "km totali", "costo totale"]


class TestParseDate:
    def test_iso_format(self):
        assert parse_date("2024-03-15") == date(2024, 3, 15)

    def test_italian_format(self):
        assert parse_date("15/03/2024") == date(2024, 3, 15)

    def test_dash_italian_format(self):
        assert parse_date("15-03-2024") == date(2024, 3, 15)

    def test_datetime_object(self):
        dt = datetime(2024, 3, 15, 10, 30)
        assert parse_date(dt) == date(2024, 3, 15)

    def test_date_object_passthrough(self):
        d = date(2024, 3, 15)
        assert parse_date(d) == d

    def test_nan_returns_none(self):
        assert parse_date(float('nan')) is None
        assert parse_date(None) is None

    def test_invalid_string_returns_none(self):
        assert parse_date("non-una-data") is None
        assert parse_date("32/13/2024") is None

    def test_datetime_string_with_time(self):
        """Stringhe come '2024-03-15 10:30:00' devono tornare solo la data."""
        assert parse_date("2024-03-15 10:30:00") == date(2024, 3, 15)

    def test_excel_timestamp(self):
        """Timestamp Pandas (come vengono da Excel)."""
        ts = pd.Timestamp("2024-03-15")
        assert parse_date(ts) == date(2024, 3, 15)


class TestParseFloat:
    def test_standard_float(self):
        assert parse_float(1.75) == 1.75

    def test_comma_decimal(self):
        assert parse_float("1,75") == 1.75

    def test_nan_returns_zero(self):
        assert parse_float(float('nan')) == 0.0
        assert parse_float(None) == 0.0

    def test_string_float(self):
        assert parse_float("123.45") == 123.45

    def test_invalid_string_returns_zero(self):
        assert parse_float("non-numero") == 0.0


class TestParseInt:
    def test_int_conversion(self):
        assert parse_int(45000) == 45000

    def test_float_truncation(self):
        assert parse_int(45000.9) == 45000

    def test_string_int(self):
        assert parse_int("45000") == 45000

    def test_float_string_truncation(self):
        """Float in stringa deve essere troncato a intero."""
        assert parse_int("45000.9") == 45000

    def test_comma_decimal_string(self):
        """Virgola come decimale (formato italiano) deve funzionare."""
        assert parse_int("45000,9") == 45000

    def test_thousands_separator_not_supported(self):
        """NOTA: Il punto come separatore migliaia NON è supportato da parse_int/parse_float.
        '45.000' viene interpretato come 45.0 (limite noto, documentato qui).
        L'utente deve usare '45000' senza separatori."""
        # Comportamento attuale (non crash, ma valore non 45000):
        result = parse_int("45.000")
        assert result == 45  # Non 45000 — limitazione nota


# =============================================================================
# TESTS: fuel.py — Logica Parse e Validazione
# =============================================================================

class TestFuelProcessFuelData:
    """Test per process_fuel_data: gestione colonne e alias map."""

    def _make_db(self, settings=None, refuelings=None):
        db = MagicMock()
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            mock_crud.get_settings.return_value = settings or _make_settings()
            mock_crud.get_all_refuelings.return_value = refuelings or []
            yield db, mock_crud

    def test_empty_dataframe_returns_empty(self):
        db = MagicMock()
        df_empty = pd.DataFrame()
        result_df, error = fuel_importer.process_fuel_data(db, USER_ID, df_empty)
        assert result_df.empty
        assert error is not None

    def test_alias_mapping_chilometri(self):
        """La colonna 'chilometri' deve mappare a 'km'."""
        db = MagicMock()
        df = pd.DataFrame({"chilometri": [50000], "data": ["2024-01-01"],
                           "prezzo": [1.75], "costo": [80.0]})
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            mock_crud.get_settings.return_value = _make_settings()
            mock_crud.get_all_refuelings.return_value = []
            result_df, error = fuel_importer.process_fuel_data(db, USER_ID, df)
        assert error is None
        assert not result_df.empty
        assert "Km" in result_df.columns

    def test_missing_litri_defaults_to_zero(self):
        """Colonna 'litri' non presente → deve defaultare a 0 (poi inferita da prezzo/costo)."""
        db = MagicMock()
        df = pd.DataFrame({"km": [50000], "data": ["2024-01-01"],
                           "prezzo": [1.75], "costo": [87.5]})
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            mock_crud.get_settings.return_value = _make_settings()
            mock_crud.get_all_refuelings.return_value = []
            result_df, _ = fuel_importer.process_fuel_data(db, USER_ID, df)
        # Litri deve essere inferito: 87.5 / 1.75 = 50.0
        assert result_df.iloc[0]["Litri"] == pytest.approx(50.0, rel=1e-2)

    def test_pieno_defaults_to_true_when_missing(self):
        db = MagicMock()
        df = pd.DataFrame({"km": [50000], "data": ["2024-01-01"],
                           "prezzo": [1.75], "costo": [87.5]})
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            mock_crud.get_settings.return_value = _make_settings()
            mock_crud.get_all_refuelings.return_value = []
            result_df, _ = fuel_importer.process_fuel_data(db, USER_ID, df)
        assert result_df.iloc[0]["Pieno"] == True

    def test_duplicate_columns_after_alias(self):
        """Se alias produce duplicati (es. 'km' e 'chilometri' entrambi presenti), non deve crashare."""
        db = MagicMock()
        df = pd.DataFrame({"km": [50000], "chilometri": [50000],
                           "data": ["2024-01-01"], "prezzo": [1.75], "costo": [87.5]})
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            mock_crud.get_settings.return_value = _make_settings()
            mock_crud.get_all_refuelings.return_value = []
            result_df, error = fuel_importer.process_fuel_data(db, USER_ID, df)
        assert error is None


class TestFuelValidation:
    """Test per validate_fuel_logic: stati, duplicati, sandwich check."""

    def _run(self, rows_data, db_refuelings=None, max_cost=200.0):
        db = MagicMock()
        df = pd.DataFrame(rows_data)
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            mock_crud.get_settings.return_value = _make_settings(max_cost)
            mock_crud.get_all_refuelings.return_value = db_refuelings or []
            result = fuel_importer.validate_fuel_logic(db, USER_ID, df)
        return result

    def test_new_record_empty_db(self):
        """Con DB vuoto, un record valido deve essere 'Nuovo'."""
        result = self._run({"data": ["2024-01-15"], "km": [50000],
                            "prezzo": [1.75], "costo": [87.5]})
        assert result.iloc[0]["Stato"] == "Nuovo"

    def test_exact_match_no_changes_is_invariant(self):
        """Record identico al DB deve essere 'Invariato'."""
        existing = _make_refueling(1, date(2024, 1, 15), 50000, cost=87.5, price=1.75, is_full=True, notes="")
        result = self._run({"data": ["2024-01-15"], "km": [50000],
                            "prezzo": [1.75], "costo": [87.5], "pieno": [True], "note": [""]},
                           db_refuelings=[existing])
        assert result.iloc[0]["Stato"] == "Invariato"

    def test_exact_match_with_cost_change_is_modifica(self):
        """Record con stessa data+km ma costo diverso deve essere 'Modifica'."""
        existing = _make_refueling(1, date(2024, 1, 15), 50000, cost=87.5, price=1.75, is_full=True)
        result = self._run({"data": ["2024-01-15"], "km": [50000],
                            "prezzo": [1.75], "costo": [95.0], "pieno": [True], "note": [""]},
                           db_refuelings=[existing])
        assert result.iloc[0]["Stato"] == "Modifica"
        assert "Costo" in result.iloc[0]["Note"]

    def test_same_date_different_km_is_error(self):
        """Nuova riga con data già presente nel DB (ma km diversi) = Errore."""
        existing = _make_refueling(1, date(2024, 1, 15), 50000)
        result = self._run({"data": ["2024-01-15"], "km": [51000],
                            "prezzo": [1.75], "costo": [87.5]},
                           db_refuelings=[existing])
        assert result.iloc[0]["Stato"] == "Errore"
        assert "Data già presente" in result.iloc[0]["Note"]

    def test_km_regression_sandwich_error(self):
        """Km inferiori al record precedente devono essere Errore."""
        prev = _make_refueling(1, date(2024, 1, 1), 50000)
        next_ = _make_refueling(2, date(2024, 2, 1), 52000)
        # Inserimento con km = 49000 (regresso rispetto al precedente)
        result = self._run({"data": ["2024-01-15"], "km": [49000],
                            "prezzo": [1.75], "costo": [87.5]},
                           db_refuelings=[prev, next_])
        assert result.iloc[0]["Stato"] == "Errore"

    def test_km_equal_to_previous_is_error(self):
        """Km uguali al record precedente devono essere Errore (odometro non può essere fermo)."""
        prev = _make_refueling(1, date(2024, 1, 1), 50000)
        result = self._run({"data": ["2024-01-15"], "km": [50000],
                            "prezzo": [1.75], "costo": [87.5]},
                           db_refuelings=[prev])
        assert result.iloc[0]["Stato"] == "Errore"

    def test_km_exceeds_next_is_error(self):
        """Km superiori al record successivo devono essere Errore."""
        prev = _make_refueling(1, date(2024, 1, 1), 50000)
        next_ = _make_refueling(2, date(2024, 2, 1), 52000)
        result = self._run({"data": ["2024-01-15"], "km": [53000],
                            "prezzo": [1.75], "costo": [87.5]},
                           db_refuelings=[prev, next_])
        assert result.iloc[0]["Stato"] == "Errore"

    def test_zero_km_is_error(self):
        """Km zero deve essere Errore."""
        result = self._run({"data": ["2024-01-15"], "km": [0],
                            "prezzo": [1.75], "costo": [87.5]})
        assert result.iloc[0]["Stato"] == "Errore"
        assert "Km zero" in result.iloc[0]["Note"] or "zero" in result.iloc[0]["Note"].lower()

    def test_cost_above_threshold_is_warning(self):
        """Costo superiore al limite impostato deve essere Warning."""
        result = self._run({"data": ["2024-01-15"], "km": [50000],
                            "prezzo": [1.75], "costo": [250.0]},
                           max_cost=200.0)
        assert result.iloc[0]["Stato"] == "Warning"

    def test_intra_file_duplicate_is_error(self):
        """Due righe con stessa data+km nello stesso file = seconda riga è Errore."""
        result = self._run({
            "data": ["2024-01-15", "2024-01-15"],
            "km": [50000, 50000],
            "prezzo": [1.75, 1.75],
            "costo": [87.5, 87.5]
        })
        stati = result["Stato"].tolist()
        assert "Errore" in stati  # La seconda riga deve essere errore
        assert stati.count("Errore") == 1

    def test_row_with_null_date_and_km_is_skipped(self):
        """Righe con data=NaN e km=0 devono essere skippate silenziosamente."""
        result = self._run({
            "data": [None, "2024-01-15"],
            "km": [0, 50000],
            "prezzo": [None, 1.75],
            "costo": [None, 87.5]
        })
        # Solo la seconda riga deve essere presente (la prima è skippata)
        assert len(result) == 1

    def test_invalid_date_is_error(self):
        """Data non parsabile = Errore."""
        result = self._run({"data": ["non-una-data"], "km": [50000],
                            "prezzo": [1.75], "costo": [87.5]})
        assert result.iloc[0]["Stato"] == "Errore"
        assert "Data invalida" in result.iloc[0]["Note"]

    def test_pieno_string_normalization(self):
        """I valori stringa per 'pieno' devono essere normalizzati correttamente."""
        result_no = self._run({"data": ["2024-01-15"], "km": [50000],
                               "prezzo": [1.75], "costo": [87.5], "pieno": ["no"]})
        assert result_no.iloc[0]["Pieno"] == False

        result_si = self._run({"data": ["2024-01-16"], "km": [51000],
                               "prezzo": [1.75], "costo": [87.5], "pieno": ["si"]})
        assert result_si.iloc[0]["Pieno"] == True

    def test_litri_inferred_from_price_and_cost(self):
        """Litri non forniti devono essere calcolati da prezzo/costo."""
        result = self._run({"data": ["2024-01-15"], "km": [50000],
                            "prezzo": [1.75], "costo": [87.5]})
        assert result.iloc[0]["Litri"] == pytest.approx(50.0, rel=1e-2)

    def test_comma_decimal_price(self):
        """Prezzi con virgola decimale devono essere parsati correttamente."""
        result = self._run({"data": ["2024-01-15"], "km": [50000],
                            "prezzo": ["1,75"], "costo": ["87,50"]})
        assert result.iloc[0]["Prezzo"] == pytest.approx(1.75)
        assert result.iloc[0]["Costo"] == pytest.approx(87.5)


class TestFuelSaveRow:
    """Test per save_row: routing Create/Update."""

    def test_save_nuovo_calls_create(self):
        db = MagicMock()
        row = {"Stato": "Nuovo", "db_id": None, "Data": date(2024,1,15),
               "Km": 50000, "Prezzo": 1.75, "Costo": 87.5, "Litri": 50.0,
               "Pieno": True, "Note_User": "Test"}
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            fuel_importer.save_row(db, USER_ID, row)
            mock_crud.create_refueling.assert_called_once()
            mock_crud.update_refueling.assert_not_called()

    def test_save_modifica_calls_update(self):
        db = MagicMock()
        row = {"Stato": "Modifica", "db_id": 42, "Data": date(2024,1,15),
               "Km": 50000, "Prezzo": 1.75, "Costo": 90.0, "Litri": 51.4,
               "Pieno": True, "Note_User": "Test"}
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            fuel_importer.save_row(db, USER_ID, row)
            mock_crud.update_refueling.assert_called_once()
            mock_crud.create_refueling.assert_not_called()

    def test_save_errore_is_skipped(self):
        db = MagicMock()
        row = {"Stato": "Errore", "db_id": None}
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            fuel_importer.save_row(db, USER_ID, row)
            mock_crud.create_refueling.assert_not_called()
            mock_crud.update_refueling.assert_not_called()

    def test_save_invariato_is_skipped(self):
        db = MagicMock()
        row = {"Stato": "Invariato", "db_id": 1}
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            fuel_importer.save_row(db, USER_ID, row)
            mock_crud.create_refueling.assert_not_called()
            mock_crud.update_refueling.assert_not_called()

    def test_save_warning_calls_create(self):
        """Righe Warning (costo alto) devono comunque essere salvate."""
        db = MagicMock()
        row = {"Stato": "Warning", "db_id": None, "Data": date(2024,1,15),
               "Km": 50000, "Prezzo": 1.75, "Costo": 250.0, "Litri": 142.8,
               "Pieno": True, "Note_User": "Pieno autostrada"}
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            fuel_importer.save_row(db, USER_ID, row)
            mock_crud.create_refueling.assert_called_once()


# =============================================================================
# TESTS: maintenance.py — Logica Parse e Validazione
# =============================================================================

class TestMaintenanceProcessData:

    def test_empty_df_returns_error(self):
        db = MagicMock()
        result_df, error = maint_importer.process_maintenance_data(db, USER_ID, pd.DataFrame())
        assert result_df.empty
        assert error is not None

    def test_missing_required_columns_returns_error(self):
        """File senza 'costo' deve tornare errore con nome colonne mancanti."""
        db = MagicMock()
        df = pd.DataFrame({"data": ["2024-01-15"], "km": [50000], "tipo": ["Tagliando"]})
        result_df, error = maint_importer.process_maintenance_data(db, USER_ID, df)
        assert result_df.empty
        assert "costo" in error.lower() or "mancanti" in error.lower()

    def test_alias_spesa_maps_to_costo(self):
        db = MagicMock()
        df = pd.DataFrame({"data": ["2024-01-15"], "km": [50000],
                           "tipo": ["Tagliando"], "spesa": [300.0]})
        with patch('src.services.data.importers.maintenance.crud') as mock_crud:
            mock_crud.get_all_maintenances.return_value = []
            result_df, error = maint_importer.process_maintenance_data(db, USER_ID, df)
        assert error is None
        assert not result_df.empty

    def test_alias_intervento_maps_to_tipo(self):
        db = MagicMock()
        df = pd.DataFrame({"data": ["2024-01-15"], "km": [50000],
                           "intervento": ["Tagliando"], "costo": [300.0]})
        with patch('src.services.data.importers.maintenance.crud') as mock_crud:
            mock_crud.get_all_maintenances.return_value = []
            result_df, error = maint_importer.process_maintenance_data(db, USER_ID, df)
        assert error is None
        assert not result_df.empty


class TestMaintenanceValidation:

    def _run(self, rows_data, db_records=None):
        db = MagicMock()
        df = pd.DataFrame(rows_data)
        with patch('src.services.data.importers.maintenance.crud') as mock_crud:
            mock_crud.get_all_maintenances.return_value = db_records or []
            result = maint_importer.validate_maintenance_logic(db, USER_ID, df)
        return result

    def test_new_record_empty_db(self):
        result = self._run({"data": ["2024-01-15"], "km": [50000],
                            "tipo": ["Tagliando"], "costo": [300.0]})
        assert result.iloc[0]["Stato"] == "Nuovo"

    def test_exact_match_by_date_km_type_is_invariant(self):
        existing = _make_maintenance(1, date(2024, 1, 15), 50000, "Tagliando", 300.0, "Testo")
        result = self._run({"data": ["2024-01-15"], "km": [50000], "tipo": ["Tagliando"],
                            "costo": [300.0], "descrizione": ["Testo"]},
                           db_records=[existing])
        assert result.iloc[0]["Stato"] == "Invariato"

    def test_match_by_id_priority_over_key(self):
        """Il match per ID ha priorità sul match per chiave logica."""
        existing = _make_maintenance(99, date(2024, 1, 15), 50000, "Tagliando", 300.0, "")
        result = self._run({"data": ["2024-01-20"], "km": [51000], "tipo": ["Tagliando"],
                            "costo": [350.0], "db_id": [99]},
                           db_records=[existing])
        assert result.iloc[0]["Stato"] == "Modifica"
        assert "Data" in result.iloc[0]["Note"]

    def test_negative_cost_is_error(self):
        result = self._run({"data": ["2024-01-15"], "km": [50000],
                            "tipo": ["Tagliando"], "costo": [-100.0]})
        assert result.iloc[0]["Stato"] == "Errore"
        assert "negativo" in result.iloc[0]["Note"].lower() or "Costo" in result.iloc[0]["Note"]

    def test_zero_km_is_error(self):
        result = self._run({"data": ["2024-01-15"], "km": [0],
                            "tipo": ["Tagliando"], "costo": [300.0]})
        assert result.iloc[0]["Stato"] == "Errore"

    def test_sandwich_check_km_below_previous(self):
        prev = _make_maintenance(1, date(2024, 1, 1), 50000)
        result = self._run({"data": ["2024-01-15"], "km": [49000],
                            "tipo": ["Tagliando"], "costo": [300.0]},
                           db_records=[prev])
        assert result.iloc[0]["Stato"] == "Errore"

    def test_intra_file_duplicate_is_error(self):
        result = self._run({
            "data": ["2024-01-15", "2024-01-15"],
            "km": [50000, 50000],
            "tipo": ["Tagliando", "Tagliando"],
            "costo": [300.0, 300.0]
        })
        stati = result["Stato"].tolist()
        assert "Errore" in stati


class TestMaintenanceSaveRow:

    def test_save_nuovo_calls_create(self):
        db = MagicMock()
        row = {"Stato": "Nuovo", "db_id": None, "Data": date(2024,1,15),
               "Km": 50000, "Tipo": "Tagliando", "Costo": 300.0, "Descrizione": "Test"}
        with patch('src.services.data.importers.maintenance.crud') as mock_crud:
            maint_importer.save_row(db, USER_ID, row)
            mock_crud.create_maintenance.assert_called_once()

    def test_save_modifica_calls_update(self):
        db = MagicMock()
        row = {"Stato": "Modifica", "db_id": 42, "Data": date(2024,1,15),
               "Km": 50000, "Tipo": "Tagliando", "Costo": 350.0, "Descrizione": "Aggiornato"}
        with patch('src.services.data.importers.maintenance.crud') as mock_crud:
            maint_importer.save_row(db, USER_ID, row)
            mock_crud.update_maintenance.assert_called_once()

    def test_save_errore_is_skipped(self):
        db = MagicMock()
        row = {"Stato": "Errore"}
        with patch('src.services.data.importers.maintenance.crud') as mock_crud:
            maint_importer.save_row(db, USER_ID, row)
            mock_crud.create_maintenance.assert_not_called()
            mock_crud.update_maintenance.assert_not_called()


# =============================================================================
# TESTS: manager.py — Orchestrazione
# =============================================================================

class TestManager:

    def test_global_error_on_invalid_excel(self):
        """File non excel/csv deve restituire global_error."""
        db = MagicMock()
        fake_file = MagicMock()
        fake_file.name = "data.xlsx"
        fake_file.read.return_value = b"not valid excel content"
        # Simula fallimento di pd.ExcelFile
        with patch('src.services.data.importers.manager.pd.ExcelFile', side_effect=Exception("Formato non valido")):
            result = manager.parse_upload_file(db, USER_ID, fake_file)
        assert "global_error" in result

    def test_no_recognized_sheets_returns_error(self):
        """Excel con fogli non riconosciuti (non 'rifornimenti'/'manutenzione') = global_error."""
        db = MagicMock()
        fake_file = MagicMock()
        fake_file.name = "data.xlsx"
        mock_xls = MagicMock()
        mock_xls.sheet_names = ["Foglio1", "Foglio2"]  # nomi non riconosciuti
        with patch('src.services.data.importers.manager.pd.ExcelFile', return_value=mock_xls):
            result = manager.parse_upload_file(db, USER_ID, fake_file)
        assert "global_error" in result
        assert "Nessun foglio" in result["global_error"]

    def test_single_unknown_sheet_assumed_fuel(self):
        """Excel con UN SOLO foglio (qualsiasi nome) deve essere trattato come Rifornimenti."""
        db = MagicMock()
        fake_file = MagicMock()
        fake_file.name = "data.xlsx"
        mock_xls = MagicMock()
        mock_xls.sheet_names = ["Sheet1"]

        with patch('src.services.data.importers.manager.pd.ExcelFile', return_value=mock_xls), \
             patch('src.services.data.importers.manager.pd.read_excel', return_value=pd.DataFrame()), \
             patch('src.services.data.importers.manager.fuel.process_fuel_data',
                   return_value=(pd.DataFrame(), "foglio vuoto")):
            result = manager.parse_upload_file(db, USER_ID, fake_file)
        assert "fuel" in result

    def test_csv_routes_to_fuel(self):
        """File CSV deve essere sempre trattato come Rifornimenti."""
        db = MagicMock()
        fake_file = MagicMock()
        fake_file.name = "data.csv"

        with patch('src.services.data.importers.manager.pd.read_csv', return_value=pd.DataFrame()), \
             patch('src.services.data.importers.manager.fuel.process_fuel_data',
                   return_value=(pd.DataFrame(), "vuoto")):
            result = manager.parse_upload_file(db, USER_ID, fake_file)
        assert "fuel" in result

    def test_sheet_name_case_insensitive(self):
        """Rilevamento foglio deve essere case-insensitive ('RIFORNIMENTI' == 'rifornimenti')."""
        db = MagicMock()
        fake_file = MagicMock()
        fake_file.name = "data.xlsx"
        mock_xls = MagicMock()
        mock_xls.sheet_names = ["RIFORNIMENTI", "MANUTENZIONE"]

        with patch('src.services.data.importers.manager.pd.ExcelFile', return_value=mock_xls), \
             patch('src.services.data.importers.manager.pd.read_excel', return_value=pd.DataFrame()), \
             patch('src.services.data.importers.manager.fuel.process_fuel_data',
                   return_value=(pd.DataFrame(), None)), \
             patch('src.services.data.importers.manager.maintenance.process_maintenance_data',
                   return_value=(pd.DataFrame(), None)):
            result = manager.parse_upload_file(db, USER_ID, fake_file)
        assert "fuel" in result
        assert "maintenance" in result


# =============================================================================
# TESTS: Nuove Validazioni (data futura, km/L anomalo)
# =============================================================================

class TestNewValidations:
    """Test per le validazioni aggiunte: data futura e consumo km/L anomalo."""

    def _run(self, rows_data, db_refuelings=None, max_cost=200.0):
        from unittest.mock import MagicMock, patch
        db = MagicMock()
        df = pd.DataFrame(rows_data)
        with patch('src.services.data.importers.fuel.crud') as mock_crud:
            mock_crud.get_settings.return_value = _make_settings(max_cost)
            mock_crud.get_all_refuelings.return_value = db_refuelings or []
            result = fuel_importer.validate_fuel_logic(db, USER_ID, df)
        return result

    def test_future_date_is_error(self):
        """Una data futura (> oggi) deve essere marcata come Errore."""
        future_date = (date.today().replace(year=date.today().year + 1)).isoformat()
        result = self._run({"data": [future_date], "km": [50000],
                            "prezzo": [1.75], "costo": [87.5]})
        assert result.iloc[0]["Stato"] == "Errore"
        assert "futuro" in result.iloc[0]["Note"].lower()

    def test_today_date_is_valid(self):
        """Una data uguale ad oggi deve essere accettata."""
        today = date.today().isoformat()
        result = self._run({"data": [today], "km": [50000],
                            "prezzo": [1.75], "costo": [87.5]})
        # Deve essere Nuovo (non Errore per la data)
        assert result.iloc[0]["Stato"] in ["Nuovo", "Warning"]
        assert "futuro" not in result.iloc[0]["Note"].lower()

    def test_anomalous_kml_extremely_high_is_error(self):
        """km/L fisicamente impossibile (>150) deve essere Errore bloccante."""
        prev = _make_refueling(1, date(2024, 1, 1), 10000)  # km precedente
        # Nuovo record: 90000 km con soli 50 litri => 80000 / 50 = 1600 km/L → ERRORE
        result = self._run(
            {"data": ["2024-06-01"], "km": [90000], "prezzo": [1.75], "costo": [87.5]},
            db_refuelings=[prev]
        )
        assert result.iloc[0]["Stato"] == "Errore"
        assert "impossibile" in result.iloc[0]["Note"].lower()

    def test_anomalous_kml_mildly_high_is_warning(self):
        """km/L leggermente fuori range (es. 55 km/L > 50 kml_max) deve essere Warning importabile."""
        prev = _make_refueling(1, date(2024, 1, 1), 50000)
        # 50000 + 55*50 = 52750 km, ma usiamo 52750 km con 50 L → 55 km/L (> 50 kml_max)
        result = self._run(
            {"data": ["2024-06-01"], "km": [52750], "prezzo": [1.75], "costo": [87.5], "litri": [50.0]},
            db_refuelings=[prev]
        )
        assert result.iloc[0]["Stato"] == "Warning"
        assert "anomalo" in result.iloc[0]["Note"].lower()

    def test_impossible_speed_is_error(self):
        """Velocità > 1500 km/giorno deve essere Errore bloccante."""
        prev = _make_refueling(1, date(2024, 1, 1), 50000)
        # 100000 km in 1 giorno → 50000 km/giorno → ERRORE
        result = self._run(
            {"data": ["2024-01-02"], "km": [100000], "prezzo": [1.75], "costo": [87.5], "litri": [50.0]},
            db_refuelings=[prev]
        )
        assert result.iloc[0]["Stato"] == "Errore"
        assert "velocit" in result.iloc[0]["Note"].lower()

    def test_anomalous_kml_low_too_is_warning(self):
        """km/L troppo basso (< 3) deve diventare Warning."""
        prev = _make_refueling(1, date(2024, 1, 1), 50000)
        # 50100 km - 50000 km = 100 delta, ma 1000 litri => 0.1 km/L
        result = self._run(
            {"data": ["2024-06-01"], "km": [50100],
             "prezzo": [0.10], "costo": [100.0], "litri": [1000.0]},
            db_refuelings=[prev]
        )
        assert result.iloc[0]["Stato"] == "Warning"

    def test_plausible_kml_stays_nuovo(self):
        """km/L plausibile (es. 15 km/L) deve rimanere Nuovo."""
        prev = _make_refueling(1, date(2024, 1, 1), 50000)
        # 50700 - 50000 = 700 km / 50 litri = 14 km/L → plausibile
        result = self._run(
            {"data": ["2024-06-01"], "km": [50700],
             "prezzo": [1.75], "costo": [87.5], "litri": [50.0]},
            db_refuelings=[prev]
        )
        assert result.iloc[0]["Stato"] == "Nuovo"
