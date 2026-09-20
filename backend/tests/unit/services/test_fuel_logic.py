"""
Tests per fuel_logic.py:
  - validate_refueling: coerenza km/data, prezzi, edge cases
  - calculate_year_kpis: aggregati annuali, anno vuoto, calcolo efficienza

Esecuzione: pytest tests/unit/services/test_fuel_logic.py -v
"""

import pytest
from datetime import date
from unittest.mock import MagicMock
from src.database.models import Refueling
from src.services.business.fuel_logic import validate_refueling, calculate_year_kpis


# =============================================================================
# HELPERS
# =============================================================================

def _refueling(r_id, d, km, cost=60.0, liters=40.0, is_full=True):
    r = MagicMock(spec=Refueling)
    r.id = r_id
    r.date = d
    r.total_km = km
    r.total_cost = cost
    r.liters = liters
    r.is_full_tank = is_full
    r.price_per_liter = round(cost / liters, 3) if liters else 0
    return r


# =============================================================================
# TEST: validate_refueling
# =============================================================================

class TestValidateRefueling:

    def _data(self, km=50000, d=None, price=1.75, cost=87.5):
        return {
            "km": km,
            "date": d or date(2024, 6, 15),
            "price": price,
            "cost": cost
        }

    # --- Controlli base ---

    def test_valid_insert_with_empty_db(self):
        is_valid, msg = validate_refueling(self._data(), all_records=[])
        assert is_valid is True
        assert msg == ""

    def test_price_zero_is_invalid(self):
        is_valid, msg = validate_refueling(self._data(price=0), all_records=[])
        assert is_valid is False
        assert "zero" in msg.lower() or "maggiori" in msg.lower()

    def test_negative_price_is_invalid(self):
        is_valid, msg = validate_refueling(self._data(price=-1.5), all_records=[])
        assert is_valid is False

    def test_cost_zero_is_invalid(self):
        is_valid, msg = validate_refueling(self._data(cost=0), all_records=[])
        assert is_valid is False

    def test_km_zero_is_invalid(self):
        is_valid, msg = validate_refueling(self._data(km=0), all_records=[])
        assert is_valid is False
        assert "chilometri" in msg.lower() or "zero" in msg.lower()

    def test_negative_km_is_invalid(self):
        is_valid, msg = validate_refueling(self._data(km=-100), all_records=[])
        assert is_valid is False

    # --- Coerenza con il passato (Prev check) ---

    def test_km_less_than_previous_is_invalid(self):
        prev = _refueling(1, date(2024, 1, 1), 52000)
        is_valid, msg = validate_refueling(
            self._data(km=50000, d=date(2024, 6, 15)),
            all_records=[prev]
        )
        assert is_valid is False
        assert "cronologico" in msg.lower() or "km" in msg.lower()

    def test_km_equal_to_previous_same_date_is_valid(self):
        """Stesso giorno: km >= prev sono permessi (due rifornimenti stessa data)."""
        prev = _refueling(1, date(2024, 6, 15), 50000)
        is_valid, msg = validate_refueling(
            self._data(km=50000, d=date(2024, 6, 15)),
            all_records=[prev]
        )
        assert is_valid is True

    def test_km_greater_than_previous_is_valid(self):
        prev = _refueling(1, date(2024, 1, 1), 48000)
        is_valid, msg = validate_refueling(
            self._data(km=50000, d=date(2024, 6, 15)),
            all_records=[prev]
        )
        assert is_valid is True

    # --- Coerenza con il futuro (Next check) ---

    def test_km_greater_than_next_is_invalid(self):
        next_ = _refueling(2, date(2025, 1, 1), 48000)
        is_valid, msg = validate_refueling(
            self._data(km=50000, d=date(2024, 6, 15)),
            all_records=[next_]
        )
        assert is_valid is False
        assert "storico" in msg.lower() or "futuro" in msg.lower() or "successivo" in msg.lower()

    def test_km_less_than_next_is_valid(self):
        next_ = _refueling(2, date(2025, 1, 1), 55000)
        is_valid, msg = validate_refueling(
            self._data(km=50000, d=date(2024, 6, 15)),
            all_records=[next_]
        )
        assert is_valid is True

    # --- Sandwich (record sia prima che dopo) ---

    def test_valid_between_prev_and_next(self):
        prev = _refueling(1, date(2024, 1, 1), 45000)
        next_ = _refueling(2, date(2025, 1, 1), 55000)
        is_valid, msg = validate_refueling(
            self._data(km=50000, d=date(2024, 6, 15)),
            all_records=[prev, next_]
        )
        assert is_valid is True

    def test_invalid_km_below_prev_with_next_present(self):
        prev = _refueling(1, date(2024, 1, 1), 52000)
        next_ = _refueling(2, date(2025, 1, 1), 60000)
        is_valid, _ = validate_refueling(
            self._data(km=50000, d=date(2024, 6, 15)),
            all_records=[prev, next_]
        )
        assert is_valid is False

    def test_invalid_km_above_next_with_prev_present(self):
        prev = _refueling(1, date(2024, 1, 1), 45000)
        next_ = _refueling(2, date(2025, 1, 1), 48000)
        is_valid, _ = validate_refueling(
            self._data(km=50000, d=date(2024, 6, 15)),
            all_records=[prev, next_]
        )
        assert is_valid is False

    def test_multiple_records_correct_neighbor_selection(self):
        """Con molti record, il validator deve scegliere i vicini CORRETTI (non il primo/ultimo)."""
        r1 = _refueling(1, date(2024, 1, 1), 40000)
        r2 = _refueling(2, date(2024, 3, 1), 43000)
        r3 = _refueling(3, date(2024, 9, 1), 54000)
        r4 = _refueling(4, date(2025, 1, 1), 60000)
        # Inserimento tra r2 e r3: km deve essere tra 43000 e 54000
        is_valid, _ = validate_refueling(
            self._data(km=48000, d=date(2024, 6, 15)),
            all_records=[r1, r2, r3, r4]
        )
        assert is_valid is True


# =============================================================================
# TEST: calculate_year_kpis
# =============================================================================

class TestCalculateYearKpis:

    def _make_records(self, specs):
        """specs: lista di (id, date, km, cost, liters, is_full)"""
        return [_refueling(*s) for s in specs]

    def test_correct_total_cost(self):
        records = self._make_records([
            (1, date(2024, 1, 1), 40000, 80.0, 45.0),
            (2, date(2024, 3, 1), 42000, 90.0, 50.0),
            (3, date(2023, 1, 1), 38000, 70.0, 40.0),  # anno diverso, deve essere escluso
        ])
        kpis = calculate_year_kpis(records, 2024)
        assert kpis["total_cost"] == pytest.approx(170.0)
        assert kpis["total_liters"] == pytest.approx(95.0)

    def test_avg_price_calculation(self):
        records = self._make_records([
            (1, date(2024, 1, 1), 40000, 88.0, 50.0),   # 88/50 = 1.76
            (2, date(2024, 6, 1), 44000, 76.5, 45.0),   # 76.5/45 = 1.70
        ])
        kpis = calculate_year_kpis(records, 2024)
        # avg_price = total_cost / total_liters = 164.5 / 95.0
        assert kpis["avg_price"] == pytest.approx(164.5 / 95.0, rel=1e-3)

    def test_km_estimation(self):
        """KM stimati = max_km - min_km nei record dell'anno."""
        records = self._make_records([
            (1, date(2024, 1, 1), 40000, 80.0, 45.0),
            (2, date(2024, 6, 1), 45000, 90.0, 50.0),
            (3, date(2024, 12, 1), 52000, 85.0, 48.0),
        ])
        kpis = calculate_year_kpis(records, 2024)
        assert kpis["km_est"] == 12000  # 52000 - 40000

    def test_empty_year_returns_zeros(self):
        """Anno senza record deve tornare tutti zeri."""
        records = self._make_records([
            (1, date(2023, 1, 1), 40000, 80.0, 45.0),
        ])
        kpis = calculate_year_kpis(records, 2024)
        assert kpis["total_cost"] == 0.0
        assert kpis["total_liters"] == 0.0
        assert kpis["avg_price"] == 0.0
        assert kpis["km_est"] == 0

    def test_single_record_km_est_is_zero(self):
        """Con un solo record non si può stimare km percorsi."""
        records = self._make_records([
            (1, date(2024, 6, 1), 50000, 80.0, 45.0),
        ])
        kpis = calculate_year_kpis(records, 2024)
        assert kpis["km_est"] == 0

    def test_view_records_filtered_correctly(self):
        records = self._make_records([
            (1, date(2024, 3, 1), 42000, 80.0, 45.0),
            (2, date(2025, 1, 1), 55000, 90.0, 50.0),  # escluso
        ])
        kpis = calculate_year_kpis(records, 2024)
        assert len(kpis["view_records"]) == 1
