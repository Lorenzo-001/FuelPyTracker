"""
Test unitari per il Router Promemoria di FastAPI (/api/reminders).
Verifica CRUD promemoria, calcolo avanzamento e scadenze, azione 'Mark as Done' e log storico.
"""
# pyrefly: ignore [missing-import]
import pytest
from datetime import date, timedelta
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

from src.api.server import app
from src.api.deps import get_db


@pytest.fixture
def client_with_db(db_session):
    """Fixture che inietta una sessione SQLite isolata nell'app FastAPI."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.pop(get_db, None)


# =============================================================================
# TEST: Creazione, Validazione e Calcolo Scadenze
# =============================================================================

def test_get_reminders_empty(client_with_db):
    """Verifica che un utente senza promemoria riceva una lista vuota."""
    response = client_with_db.get("/api/reminders", headers={"X-User-Id": "user-rem-0"})
    assert response.status_code == 200
    assert response.json() == []


def test_create_reminder_km_and_days(client_with_db):
    """Verifica la creazione di promemoria a chilometri e a tempo."""
    headers = {"X-User-Id": "user-rem-create"}

    # 1. Promemoria a Km
    res_km = client_with_db.post("/api/reminders", json={
        "title": "Controllo Olio Motore",
        "frequency_km": 10000,
        "current_km": 50000,
        "notes": "Controllare livello a freddo",
    }, headers=headers)
    assert res_km.status_code == 201
    data_km = res_km.json()
    assert data_km["title"] == "Controllo Olio Motore"
    assert data_km["frequency_km"] == 10000
    assert data_km["target_km"] == 60000
    assert data_km["remaining_km"] == 10000
    assert data_km["progress"] == 0.0
    assert data_km["is_overdue"] is False

    # 2. Promemoria a Giorni
    res_days = client_with_db.post("/api/reminders", json={
        "title": "Pressione Pneumatici",
        "frequency_days": 30,
    }, headers=headers)
    assert res_days.status_code == 201
    data_days = res_days.json()
    assert data_days["title"] == "Pressione Pneumatici"
    assert data_days["frequency_days"] == 30
    assert data_days["remaining_days"] == 30
    assert data_days["is_overdue"] is False


def test_create_reminder_missing_frequency(client_with_db):
    """Verifica che la creazione senza né km né giorni venga rifiutata con HTTP 422."""
    headers = {"X-User-Id": "user-rem-val"}
    response = client_with_db.post("/api/reminders", json={
        "title": "Controllo Invalido",
    }, headers=headers)
    assert response.status_code == 422


def test_reminder_overdue_detection(client_with_db):
    """Verifica il calcolo corretto dello stato di superamento limite (is_overdue=True)."""
    headers = {"X-User-Id": "user-rem-overdue"}

    # Creiamo promemoria con check a 50.000 Km ogni 5.000 Km
    client_with_db.post("/api/reminders", json={
        "title": "Controllo Freni",
        "frequency_km": 5000,
        "current_km": 50000,
    }, headers=headers)

    # Aggiungiamo un rifornimento a 56.000 Km (limite era 55.000 -> superato di 1.000 Km)
    client_with_db.post("/api/fuel", json={
        "date": "2025-07-01",
        "total_km": 56000,
        "price_per_liter": 1.80,
        "total_cost": 50.0,
        "liters": 27.78,
        "is_full_tank": True,
    }, headers=headers)

    res = client_with_db.get("/api/reminders", headers=headers)
    assert res.status_code == 200
    rems = res.json()
    assert len(rems) == 1
    rem = rems[0]
    assert rem["is_overdue"] is True
    assert rem["remaining_km"] == -1000
    assert rem["progress"] == 1.0
    assert "superato da 1000 Km" in rem["status_message"]


# =============================================================================
# TEST: Mark as Done & Storico Esecuzioni
# =============================================================================

def test_complete_reminder_mark_as_done(client_with_db):
    """Verifica l'azione 'Mark as Done', il reset del target e il log nello storico."""
    headers = {"X-User-Id": "user-rem-complete"}

    # Creazione
    created = client_with_db.post("/api/reminders", json={
        "title": "Rabbocco Liquido Lavavetri",
        "frequency_days": 60,
    }, headers=headers).json()
    rem_id = created["id"]

    # Esecuzione 'Mark as Done'
    comp_res = client_with_db.post(
        f"/api/reminders/{rem_id}/complete",
        json={"check_date": "2025-08-01", "check_km": 52000, "notes": "Rabboccato con antigelo"},
        headers=headers,
    )
    assert comp_res.status_code == 200
    upd_rem = comp_res.json()
    assert upd_rem["last_km_check"] == 52000
    assert upd_rem["last_date_check"] == "2025-08-01"

    # Verifica presenza nel log storico
    hist_res = client_with_db.get("/api/reminders/history", headers=headers)
    assert hist_res.status_code == 200
    logs = hist_res.json()
    assert len(logs) == 1
    assert logs[0]["reminder_id"] == rem_id
    assert logs[0]["notes"] == "Rabboccato con antigelo"


def test_complete_overdue_reminder_resets_cycle(client_with_db):
    """Verifica che l'azione 'Mark as Done' su un promemoria con limite superato (is_overdue=True)
    azzeri correttamente il ciclo calcolando il nuovo target a partire dal chilometraggio attuale del veicolo."""
    headers = {"X-User-Id": "user-rem-overdue-reset"}

    # 1. Crea promemoria chilometrico con check a 50.000 Km ogni 5.000 Km (scadenza prevista a 55.000)
    created = client_with_db.post("/api/reminders", json={
        "title": "Controllo Pastiglie Freni",
        "frequency_km": 5000,
        "current_km": 50000,
    }, headers=headers).json()
    rem_id = created["id"]

    # 2. Registra rifornimento a 57.000 Km (il limite di 55.000 è superato da 2.000 Km)
    client_with_db.post("/api/fuel", json={
        "date": "2026-09-20",
        "total_km": 57000,
        "price_per_liter": 1.80,
        "total_cost": 60.0,
        "liters": 33.33,
        "is_full_tank": True,
    }, headers=headers)

    # 3. Verifica che il promemoria sia attualmente SCADUTO
    res_before = client_with_db.get("/api/reminders", headers=headers)
    assert res_before.status_code == 200
    rem_before = [r for r in res_before.json() if r["id"] == rem_id][0]
    assert rem_before["is_overdue"] is True
    assert rem_before["remaining_km"] == -2000
    assert rem_before["progress"] == 1.0

    # 4. Esegue il completamento senza specificare check_km (il pulsante rapido dell'UI azzera al km attuale)
    comp_res = client_with_db.post(
        f"/api/reminders/{rem_id}/complete",
        json={"check_date": "2026-09-24", "notes": "Eseguito controllo freni"},
        headers=headers,
    )
    assert comp_res.status_code == 200
    rem_after = comp_res.json()

    # 5. Verifica che il ciclo sia AZZERATO con successo partendo da 57.000 Km
    assert rem_after["last_km_check"] == 57000
    assert rem_after["target_km"] == 62000  # 57.000 + 5.000
    assert rem_after["remaining_km"] == 5000
    assert rem_after["progress"] == 0.0
    assert rem_after["is_overdue"] is False



# =============================================================================
# TEST: Update, Delete & Tenant Isolation
# =============================================================================

def test_reminders_crud_and_tenant_isolation(client_with_db):
    """Verifica dettaglio, modifica, eliminazione e isolamento multi-tenant dei promemoria."""
    headers_a = {"X-User-Id": "user-charlie"}
    headers_b = {"X-User-Id": "user-dave"}

    created = client_with_db.post("/api/reminders", json={
        "title": "Filtro Antipolline",
        "frequency_km": 15000,
        "current_km": 30000,
    }, headers=headers_a).json()
    rem_id = created["id"]

    # Charlie accede al proprio promemoria (200)
    assert client_with_db.get(f"/api/reminders/{rem_id}", headers=headers_a).status_code == 200

    # Dave tenta di accedere al promemoria di Charlie (404)
    assert client_with_db.get(f"/api/reminders/{rem_id}", headers=headers_b).status_code == 404

    # Charlie aggiorna le note
    upd = client_with_db.put(f"/api/reminders/{rem_id}", json={"notes": "Nuovo filtro ai carboni"}, headers=headers_a)
    assert upd.status_code == 200
    assert upd.json()["notes"] == "Nuovo filtro ai carboni"

    # Dave tenta di completare o eliminare il promemoria di Charlie (404)
    assert client_with_db.post(f"/api/reminders/{rem_id}/complete", json={"check_km": 35000}, headers=headers_b).status_code == 404
    assert client_with_db.delete(f"/api/reminders/{rem_id}", headers=headers_b).status_code == 404

    # Charlie elimina il promemoria
    del_res = client_with_db.delete(f"/api/reminders/{rem_id}", headers=headers_a)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True
    assert client_with_db.get(f"/api/reminders/{rem_id}", headers=headers_a).status_code == 404
