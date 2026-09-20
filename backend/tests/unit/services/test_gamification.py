"""
Tests per gamification.py — calculate_car_health_score

Copre: score base, penalità manutenzioni (Km e Data), penalità reminder,
       cap a 0, nessuna scadenza, combinazioni multiple.

Esecuzione: pytest tests/unit/services/test_gamification.py -v
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from src.services.business.gamification import calculate_car_health_score


# =============================================================================
# HELPERS
# =============================================================================

TODAY = date.today()

def _make_maintenance(m_id, expense_type, expiry_km=None, expiry_date=None):
    m = MagicMock()
    m.id = m_id
    m.expense_type = expense_type
    m.expiry_km = expiry_km
    m.expiry_date = expiry_date
    return m

def _make_reminder(r_id, title, freq_km=None, freq_days=None,
                   last_km=0, last_date=None):
    r = MagicMock()
    r.id = r_id
    r.title = title
    r.frequency_km = freq_km
    r.frequency_days = freq_days
    r.last_km_check = last_km
    r.last_date_check = last_date or TODAY
    return r

def _run(maintenances, reminders, current_km=50000):
    db = MagicMock()
    with patch('src.services.business.gamification.crud') as mock_crud:
        mock_crud.get_all_active_deadlines.return_value = maintenances
        mock_crud.get_active_reminders.return_value = reminders
        return calculate_car_health_score(db, "user-id", current_km)


# =============================================================================
# TEST: Score Perfetto (nessuna scadenza)
# =============================================================================

class TestCarHealthScorePerfect:

    def test_no_deadlines_no_reminders_score_100(self):
        score, items = _run([], [])
        assert score == 100
        assert items == []

    def test_maintenance_not_expired_km_score_100(self):
        """Manutenzione con scadenza futura (km non ancora raggiunti)."""
        m = _make_maintenance(1, "Tagliando", expiry_km=60000)  # km ora: 50000
        score, items = _run([m], [], current_km=50000)
        assert score == 100

    def test_maintenance_not_expired_date_score_100(self):
        """Manutenzione con data di scadenza nel futuro."""
        m = _make_maintenance(1, "Bollo", expiry_date=TODAY + timedelta(days=30))
        score, items = _run([m], [])
        assert score == 100

    def test_reminder_not_expired_km_score_100(self):
        """Reminder km non ancora scaduto."""
        r = _make_reminder(1, "Olio", freq_km=2000, last_km=49000)
        score, items = _run([], [r], current_km=50000)  # diff = 1000 < 2000
        assert score == 100

    def test_reminder_not_expired_days_score_100(self):
        """Reminder giorni non ancora scaduto."""
        r = _make_reminder(1, "Pressione", freq_days=30, last_date=TODAY - timedelta(days=10))
        score, items = _run([], [r])
        assert score == 100


# =============================================================================
# TEST: Penalità Manutenzione
# =============================================================================

class TestCarHealthScoreMaintenancePenalties:

    def test_expired_km_penalty_20(self):
        """Manutenzione meccanica scaduta per km: -20 punti."""
        m = _make_maintenance(1, "Tagliando", expiry_km=48000)  # km ora: 50000 → scaduto
        score, items = _run([m], [], current_km=50000)
        assert score == 80
        assert any("Tagliando" in i for i in items)

    def test_expired_date_penalty_15(self):
        """Manutenzione scaduta per data: -15 punti."""
        m = _make_maintenance(1, "Revisione", expiry_date=TODAY - timedelta(days=10))
        score, items = _run([m], [])
        assert score == 85
        assert any("Revisione" in i for i in items)

    def test_multiple_expired_maintenances(self):
        """Due manutenzioni scadute: -20 - 15 = -35."""
        m1 = _make_maintenance(1, "Tagliando", expiry_km=45000)  # scaduto km
        m2 = _make_maintenance(2, "Bollo", expiry_date=TODAY - timedelta(days=5))  # scaduto data
        score, items = _run([m1, m2], [], current_km=50000)
        assert score == 65
        assert len(items) == 2

    def test_km_check_takes_priority_over_date_check(self):
        """Se la manutenzione è scaduta per km (elif per data → non duplica penalità)."""
        # expiry_km scaduto → prende malus km (-20), NON entra nell'elif data
        m = _make_maintenance(1, "Tagliando", expiry_km=48000, expiry_date=TODAY - timedelta(days=1))
        score, items = _run([m], [], current_km=50000)
        assert score == 80  # Solo -20, non -20-15
        assert len(items) == 1


# =============================================================================
# TEST: Penalità Reminder
# =============================================================================

class TestCarHealthScoreReminderPenalties:

    def test_expired_reminder_km_penalty_10(self):
        """Reminder km scaduto: -10 punti."""
        r = _make_reminder(1, "Olio", freq_km=2000, last_km=47000)  # diff=3000 > 2000
        score, items = _run([], [r], current_km=50000)
        assert score == 90
        assert any("Olio" in i for i in items)

    def test_expired_reminder_days_penalty_5(self):
        """Reminder giorni scaduto: -5 punti."""
        r = _make_reminder(1, "Pressione", freq_days=30, last_date=TODAY - timedelta(days=40))
        score, items = _run([], [r])
        assert score == 95
        assert any("Pressione" in i for i in items)

    def test_multiple_reminder_penalties(self):
        r1 = _make_reminder(1, "Olio", freq_km=2000, last_km=47000)
        r2 = _make_reminder(2, "Filtro", freq_days=180, last_date=TODAY - timedelta(days=200))
        score, items = _run([], [r1, r2], current_km=50000)
        assert score == 85  # -10 -5 = -15
        assert len(items) == 2


# =============================================================================
# TEST: Combinazioni e Cap
# =============================================================================

class TestCarHealthScoreCombinedAndCap:

    def test_combined_maintenance_and_reminder_penalties(self):
        """Manutenzione km scaduta + reminder giorni scaduto."""
        m = _make_maintenance(1, "Tagliando", expiry_km=48000)
        r = _make_reminder(1, "Pressione", freq_days=30, last_date=TODAY - timedelta(days=40))
        score, items = _run([m], [r], current_km=50000)
        assert score == 75  # 100 - 20 - 5
        assert len(items) == 2

    def test_score_capped_at_zero(self):
        """Con molte scadenze, il punteggio non può scendere sotto 0."""
        maintenances = [
            _make_maintenance(i, f"Tipo{i}", expiry_km=40000)
            for i in range(1, 8)   # 7 × 20 = 140 malus
        ]
        score, _ = _run(maintenances, [], current_km=50000)
        assert score == 0

    def test_score_never_exceeds_100(self):
        """Il punteggio non deve mai superare 100."""
        score, _ = _run([], [])
        assert score <= 100

    def test_overdue_items_list_is_descriptive(self):
        """Gli elementi nella lista overdue devono contenere il tipo di scadenza."""
        m = _make_maintenance(1, "Gomme", expiry_km=48000)
        _, items = _run([m], [], current_km=50000)
        assert len(items) == 1
        assert "Gomme" in items[0]
        assert "Km" in items[0] or "km" in items[0].lower()
