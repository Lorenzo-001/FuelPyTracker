"""
Tests per maintenance_logic.py — funzioni di filtro e aggregazione

Copre: get_available_years, filter_records_by_year, filter_records_by_category,
       get_all_categories.

Esecuzione: pytest tests/unit/services/test_maintenance_logic.py -v
"""

import pytest
from datetime import date
from unittest.mock import MagicMock
from src.services.business.maintenance_logic import (
    get_available_years,
    filter_records_by_year,
    filter_records_by_category,
    get_all_categories
)


# =============================================================================
# HELPERS
# =============================================================================

def _rec(d, expense_type="Tagliando"):
    r = MagicMock()
    r.date = d
    r.expense_type = expense_type
    return r


# =============================================================================
# TEST: get_available_years
# =============================================================================

class TestGetAvailableYears:

    def test_multiple_years_sorted_descending(self):
        recs = [_rec(date(2022, 1, 1)), _rec(date(2024, 6, 1)), _rec(date(2023, 3, 1))]
        years = get_available_years(recs)
        assert years == sorted(years, reverse=True)
        assert 2024 in years and 2023 in years and 2022 in years

    def test_empty_list_returns_current_year(self):
        years = get_available_years([])
        assert years == [date.today().year]

    def test_duplicate_years_deduplicated(self):
        recs = [_rec(date(2024, 1, 1)), _rec(date(2024, 6, 1)), _rec(date(2024, 12, 1))]
        years = get_available_years(recs)
        assert years.count(2024) == 1

    def test_single_year_record(self):
        recs = [_rec(date(2023, 5, 15))]
        years = get_available_years(recs)
        assert 2023 in years


# =============================================================================
# TEST: filter_records_by_year
# =============================================================================

class TestFilterRecordsByYear:

    def _records(self):
        return [
            _rec(date(2022, 3, 1)),
            _rec(date(2023, 7, 1)),
            _rec(date(2024, 1, 1)),
            _rec(date(2024, 11, 1)),
        ]

    def test_filter_specific_year(self):
        recs = self._records()
        filtered, label = filter_records_by_year(recs, 2024)
        assert len(filtered) == 2
        assert label == "2024"

    def test_filter_tutti_gli_anni(self):
        recs = self._records()
        filtered, label = filter_records_by_year(recs, "Tutti gli anni")
        assert len(filtered) == 4
        assert label == "storico"

    def test_filter_year_with_no_records(self):
        recs = self._records()
        filtered, label = filter_records_by_year(recs, 2020)
        assert filtered == []
        assert label == "2020"

    def test_filter_single_year_record(self):
        recs = [_rec(date(2023, 5, 1))]
        filtered, label = filter_records_by_year(recs, 2023)
        assert len(filtered) == 1


# =============================================================================
# TEST: filter_records_by_category
# =============================================================================

class TestFilterRecordsByCategory:

    def _records(self):
        return [
            _rec(date(2024, 1, 1), "Tagliando"),
            _rec(date(2024, 2, 1), "Gomme"),
            _rec(date(2024, 3, 1), "Bollo"),
            _rec(date(2024, 4, 1), "Tagliando"),
        ]

    def test_filter_single_category(self):
        filtered = filter_records_by_category(self._records(), ["Tagliando"])
        assert len(filtered) == 2
        assert all(r.expense_type == "Tagliando" for r in filtered)

    def test_filter_multiple_categories(self):
        filtered = filter_records_by_category(self._records(), ["Tagliando", "Bollo"])
        assert len(filtered) == 3

    def test_empty_categories_returns_all(self):
        """Lista categorie vuota = nessun filtro applicato."""
        recs = self._records()
        filtered = filter_records_by_category(recs, [])
        assert len(filtered) == len(recs)

    def test_category_not_present_returns_empty(self):
        filtered = filter_records_by_category(self._records(), ["Batteria"])
        assert filtered == []

    def test_none_categories_returns_all(self):
        """None come lista categorie = nessun filtro."""
        recs = self._records()
        filtered = filter_records_by_category(recs, None)
        assert len(filtered) == len(recs)


# =============================================================================
# TEST: get_all_categories
# =============================================================================

class TestGetAllCategories:

    def test_unique_categories_sorted(self):
        recs = [
            _rec(date(2024, 1, 1), "Tagliando"),
            _rec(date(2024, 2, 1), "Gomme"),
            _rec(date(2024, 3, 1), "Tagliando"),   # duplicato
            _rec(date(2024, 4, 1), "Bollo"),
        ]
        cats = get_all_categories(recs)
        assert sorted(cats) == cats              # deve essere ordinato
        assert len(cats) == 3                    # deduplicato
        assert "Tagliando" in cats

    def test_empty_records_returns_empty(self):
        cats = get_all_categories([])
        assert cats == []

    def test_single_category(self):
        recs = [_rec(date(2024, 1, 1), "Tagliando")]
        cats = get_all_categories(recs)
        assert cats == ["Tagliando"]
