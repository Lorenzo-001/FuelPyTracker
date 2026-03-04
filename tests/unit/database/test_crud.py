"""
Tests per database/crud.py

Copre: create/read/update/delete per Refueling, Maintenance, Reminder.
Usa DB SQLite in memoria (via conftest.py).

Esecuzione: pytest tests/unit/database/test_crud.py -v
"""

from datetime import date
from src.database import crud

USER_ID = "test-user-uuid"
OTHER_USER = "other-user-uuid"


# =============================================================================
# TESTS: Refueling CRUD
# =============================================================================

class TestRefuelingCrud:

    def test_create_and_retrieve_refueling(self, db_session):
        """Create + GetAll: persistenza base e filtro per utente."""
        r = crud.create_refueling(
            db=db_session, user_id=USER_ID,
            date_obj=date(2025, 1, 1), total_km=50000,
            price_per_liter=1.80, total_cost=90.00,
            liters=50.0, is_full_tank=True, notes="Test create"
        )
        assert r.id is not None
        assert r.total_km == 50000

        records = crud.get_all_refuelings(db_session, USER_ID)
        assert len(records) == 1
        assert records[0].notes == "Test create"

    def test_user_isolation_refueling(self, db_session):
        """Record di un altro utente non devono apparire nel get dell'utente corrente."""
        crud.create_refueling(db=db_session, user_id=USER_ID,
            date_obj=date(2025, 1, 1), total_km=50000,
            price_per_liter=1.80, total_cost=90.0, liters=50.0, is_full_tank=True)
        crud.create_refueling(db=db_session, user_id=OTHER_USER,
            date_obj=date(2025, 1, 2), total_km=60000,
            price_per_liter=1.85, total_cost=92.0, liters=49.7, is_full_tank=True)

        records = crud.get_all_refuelings(db_session, USER_ID)
        assert len(records) == 1  # Solo il record dell'utente corrente

    def test_update_refueling(self, db_session):
        """Update: verifica che solo i campi indicati vengano modificati."""
        r = crud.create_refueling(db=db_session, user_id=USER_ID,
            date_obj=date(2025, 1, 1), total_km=50000,
            price_per_liter=1.80, total_cost=90.0, liters=50.0, is_full_tank=True)

        crud.update_refueling(db_session, USER_ID, r.id, {
            "total_cost": 95.0, "notes": "Aggiornato"
        })

        updated = crud.get_all_refuelings(db_session, USER_ID)
        assert updated[0].total_cost == 95.0
        assert updated[0].notes == "Aggiornato"
        assert updated[0].total_km == 50000  # Campo non toccato

    def test_update_refueling_wrong_user_is_noop(self, db_session):
        """Update di un record non appartenente all'utente non deve avere effetto."""
        r = crud.create_refueling(db=db_session, user_id=USER_ID,
            date_obj=date(2025, 1, 1), total_km=50000,
            price_per_liter=1.80, total_cost=90.0, liters=50.0, is_full_tank=True)

        crud.update_refueling(db_session, OTHER_USER, r.id, {"total_cost": 999.0})

        untouched = crud.get_all_refuelings(db_session, USER_ID)
        assert untouched[0].total_cost == 90.0  # Non modificato

    def test_delete_refueling(self, db_session):
        """Delete: il record deve scomparire dal DB."""
        r = crud.create_refueling(db=db_session, user_id=USER_ID,
            date_obj=date(2025, 1, 1), total_km=50000,
            price_per_liter=1.80, total_cost=90.0, liters=50.0, is_full_tank=True)

        crud.delete_refueling(db_session, USER_ID, r.id)

        records = crud.get_all_refuelings(db_session, USER_ID)
        assert len(records) == 0

    def test_delete_refueling_wrong_user_is_noop(self, db_session):
        """Delete di un record di un altro utente non deve rimuovere nullala."""
        r = crud.create_refueling(db=db_session, user_id=USER_ID,
            date_obj=date(2025, 1, 1), total_km=50000,
            price_per_liter=1.80, total_cost=90.0, liters=50.0, is_full_tank=True)

        crud.delete_refueling(db_session, OTHER_USER, r.id)

        records = crud.get_all_refuelings(db_session, USER_ID)
        assert len(records) == 1  # Non eliminato

    def test_get_last_refueling(self, db_session):
        """get_last_refueling deve restituire il record con km massimi."""
        crud.create_refueling(db=db_session, user_id=USER_ID,
            date_obj=date(2024, 1, 1), total_km=40000,
            price_per_liter=1.75, total_cost=87.5, liters=50.0, is_full_tank=True)
        crud.create_refueling(db=db_session, user_id=USER_ID,
            date_obj=date(2025, 1, 1), total_km=55000,
            price_per_liter=1.80, total_cost=90.0, liters=50.0, is_full_tank=True)

        last = crud.get_last_refueling(db_session, USER_ID)
        assert last.total_km == 55000

    def test_get_last_refueling_single_record_returns_it(self, db_session):
        """Con un solo record, get_last_refueling deve restituirlo."""
        crud.create_refueling(db=db_session, user_id=USER_ID,
            date_obj=date(2025, 3, 1), total_km=60000,
            price_per_liter=1.80, total_cost=90.0, liters=50.0, is_full_tank=True)

        last = crud.get_last_refueling(db_session, USER_ID)
        assert last is not None
        assert last.total_km == 60000


# =============================================================================
# TESTS: Maintenance CRUD
# =============================================================================

class TestMaintenanceCrud:

    def test_create_and_retrieve_maintenance(self, db_session):
        m = crud.create_maintenance(
            db=db_session, user_id=USER_ID,
            date_obj=date(2025, 2, 1), total_km=51000,
            expense_type="Tagliando", cost=400.0,
            description="Cambio olio motore"
        )
        assert m.id is not None
        assert m.expense_type == "Tagliando"
        assert m.cost == 400.0

        records = crud.get_all_maintenances(db_session, USER_ID)
        assert len(records) == 1
        assert records[0].description == "Cambio olio motore"

    def test_create_maintenance_with_expiry(self, db_session):
        """Manutenzione con scadenza km e data."""
        m = crud.create_maintenance(
            db=db_session, user_id=USER_ID,
            date_obj=date(2025, 2, 1), total_km=51000,
            expense_type="Gomme", cost=600.0,
            expiry_km=61000, expiry_date=date(2026, 2, 1)
        )
        assert m.expiry_km == 61000
        assert m.expiry_date == date(2026, 2, 1)

    def test_user_isolation_maintenance(self, db_session):
        crud.create_maintenance(db=db_session, user_id=USER_ID,
            date_obj=date(2025, 2, 1), total_km=51000,
            expense_type="Tagliando", cost=400.0)
        crud.create_maintenance(db=db_session, user_id=OTHER_USER,
            date_obj=date(2025, 3, 1), total_km=60000,
            expense_type="Gomme", cost=600.0)

        records = crud.get_all_maintenances(db_session, USER_ID)
        assert len(records) == 1

    def test_update_maintenance(self, db_session):
        m = crud.create_maintenance(db=db_session, user_id=USER_ID,
            date_obj=date(2025, 2, 1), total_km=51000,
            expense_type="Tagliando", cost=400.0)

        crud.update_maintenance(db_session, USER_ID, m.id, {
            "cost": 450.0, "description": "Aggiornato"
        })

        records = crud.get_all_maintenances(db_session, USER_ID)
        assert records[0].cost == 450.0
        assert records[0].description == "Aggiornato"

    def test_delete_maintenance(self, db_session):
        m = crud.create_maintenance(db=db_session, user_id=USER_ID,
            date_obj=date(2025, 2, 1), total_km=51000,
            expense_type="Tagliando", cost=400.0)

        crud.delete_maintenance(db_session, USER_ID, m.id)

        records = crud.get_all_maintenances(db_session, USER_ID)
        assert len(records) == 0


# =============================================================================
# TESTS: Reminder CRUD
# =============================================================================

class TestReminderCrud:

    def test_create_and_retrieve_reminder(self, db_session):
        r = crud.create_reminder(
            db=db_session, user_id=USER_ID,
            title="Cambio Olio",
            frequency_km=10000, frequency_days=None,
            current_km=50000, current_date=date(2025, 1, 1)
        )
        assert r.id is not None
        assert r.title == "Cambio Olio"
        assert r.frequency_km == 10000

        reminders = crud.get_active_reminders(db_session, USER_ID)
        assert len(reminders) == 1

    def test_create_reminder_days_based(self, db_session):
        r = crud.create_reminder(
            db=db_session, user_id=USER_ID,
            title="Verifica Pressione",
            frequency_km=None, frequency_days=30,
            current_km=50000, current_date=date(2025, 1, 1)
        )
        assert r.frequency_days == 30
        assert r.frequency_km is None

    def test_log_reminder_execution(self, db_session):
        """Mark as done: deve creare log e aggiornare last_km_check/last_date_check."""
        r = crud.create_reminder(
            db=db_session, user_id=USER_ID,
            title="Cambio Olio",
            frequency_km=10000, frequency_days=None,
            current_km=50000, current_date=date(2025, 1, 1)
        )

        crud.log_reminder_execution(
            db=db_session, user_id=USER_ID, reminder_id=r.id,
            check_date=date(2025, 6, 1), check_km=55000, notes="Fatto"
        )

        # Verifica aggiornamento last check
        reminders = crud.get_active_reminders(db_session, USER_ID)
        assert reminders[0].last_km_check == 55000
        assert reminders[0].last_date_check == date(2025, 6, 1)

    def test_update_reminder(self, db_session):
        r = crud.create_reminder(
            db=db_session, user_id=USER_ID,
            title="Cambio Olio", frequency_km=10000, frequency_days=None,
            current_km=50000, current_date=date(2025, 1, 1)
        )

        crud.update_reminder(
            db=db_session, user_id=USER_ID, reminder_id=r.id,
            title="Cambio Olio Nuovo", freq_km=15000, freq_days=365, notes="Aggiornato"
        )

        reminders = crud.get_active_reminders(db_session, USER_ID)
        assert reminders[0].title == "Cambio Olio Nuovo"
        assert reminders[0].frequency_km == 15000

    def test_delete_reminder(self, db_session):
        r = crud.create_reminder(
            db=db_session, user_id=USER_ID,
            title="Cambio Olio", frequency_km=10000, frequency_days=None,
            current_km=50000, current_date=date(2025, 1, 1)
        )

        crud.delete_reminder(db_session, USER_ID, r.id)

        reminders = crud.get_active_reminders(db_session, USER_ID)
        assert len(reminders) == 0

    def test_user_isolation_reminders(self, db_session):
        crud.create_reminder(db=db_session, user_id=USER_ID,
            title="Olio", frequency_km=10000, frequency_days=None,
            current_km=50000, current_date=date(2025, 1, 1))
        crud.create_reminder(db=db_session, user_id=OTHER_USER,
            title="Filtro", frequency_km=20000, frequency_days=None,
            current_km=60000, current_date=date(2025, 1, 1))

        reminders = crud.get_active_reminders(db_session, USER_ID)
        assert len(reminders) == 1
        assert reminders[0].title == "Olio"