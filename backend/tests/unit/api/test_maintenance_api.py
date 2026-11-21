"""
Test unitari per il Router Manutenzione di FastAPI (/api/maintenance).
Verifica CRUD interventi, filtri per anno/categoria, scadenze predittive e tenant isolation.
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
# TEST: CRUD Base e Validazione Pydantic
# =============================================================================

def test_get_maintenances_empty(client_with_db):
    """Verifica che un utente senza record riceva una lista vuota."""
    response = client_with_db.get("/api/maintenance", headers={"X-User-Id": "user-maint-0"})
    assert response.status_code == 200
    assert response.json() == []


def test_create_maintenance_success(client_with_db):
    """Verifica la creazione con successo di un intervento di manutenzione."""
    headers = {"X-User-Id": "user-maint-1"}
    payload = {
        "date": "2025-05-15",
        "total_km": 60000,
        "expense_type": "Tagliando",
        "cost": 280.50,
        "description": "Cambio olio e tutti i filtri",
        "expiry_km": 80000,
        "expiry_date": "2026-05-15",
    }
    response = client_with_db.post("/api/maintenance", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["user_id"] == "user-maint-1"
    assert data["expense_type"] == "Tagliando"
    assert data["cost"] == 280.50
    assert data["expiry_km"] == 80000
    assert data["expiry_date"] == "2026-05-15"


def test_create_maintenance_validation_pydantic(client_with_db):
    """Verifica che valori negativi vengano respinti con HTTP 422."""
    headers = {"X-User-Id": "user-maint-1"}
    response = client_with_db.post("/api/maintenance", json={
        "date": "2025-05-15",
        "total_km": -50,  # Non ammesso
        "expense_type": "Tagliando",
        "cost": -10.0,    # Non ammesso
    }, headers=headers)
    assert response.status_code == 422


def test_get_maintenances_filters(client_with_db):
    """Verifica i filtri per anno solare e categoria di spesa."""
    headers = {"X-User-Id": "user-maint-filters"}

    # Record 2024: Bollo
    client_with_db.post("/api/maintenance", json={
        "date": "2024-02-10",
        "total_km": 40000,
        "expense_type": "Bollo",
        "cost": 210.0,
    }, headers=headers)

    # Record 2025: Tagliando
    client_with_db.post("/api/maintenance", json={
        "date": "2025-04-10",
        "total_km": 55000,
        "expense_type": "Tagliando",
        "cost": 320.0,
    }, headers=headers)

    # Filtro per anno 2025
    res_2025 = client_with_db.get("/api/maintenance?year=2025", headers=headers)
    assert res_2025.status_code == 200
    assert len(res_2025.json()) == 1
    assert res_2025.json()[0]["expense_type"] == "Tagliando"

    # Filtro per categoria 'Bollo'
    res_bollo = client_with_db.get("/api/maintenance?expense_type=Bollo", headers=headers)
    assert res_bollo.status_code == 200
    assert len(res_bollo.json()) == 1
    assert res_bollo.json()[0]["expense_type"] == "Bollo"


def test_get_categories(client_with_db):
    """Verifica il recupero delle categorie uniche utilizzate dall'utente."""
    headers = {"X-User-Id": "user-maint-cats"}
    client_with_db.post("/api/maintenance", json={
        "date": "2025-01-10", "total_km": 50000, "expense_type": "Gomme", "cost": 400.0,
    }, headers=headers)
    client_with_db.post("/api/maintenance", json={
        "date": "2025-03-10", "total_km": 52000, "expense_type": "Tagliando", "cost": 250.0,
    }, headers=headers)

    res = client_with_db.get("/api/maintenance/categories", headers=headers)
    assert res.status_code == 200
    cats = res.json()
    assert "Gomme" in cats
    assert "Tagliando" in cats


def test_create_custom_maintenance_category_and_filter(client_with_db):
    """Verifica la creazione di un intervento con categoria personalizzata ('Altro' specificato),
    la sua inclusione nelle categorie distinte e il filtraggio esatto via query param."""
    headers = {"X-User-Id": "user-custom-category"}

    # Registra una manutenzione con tipologia custom (max 20 caratteri)
    custom_type = "Tergicristalli"
    res_create = client_with_db.post("/api/maintenance", json={
        "date": "2026-09-24",
        "total_km": 125000,
        "expense_type": custom_type,
        "cost": 35.0,
        "description": "Sostituzione spazzole tergicristallo Bosch Aerotwin",
    }, headers=headers)
    assert res_create.status_code == 201
    created_data = res_create.json()
    assert created_data["expense_type"] == "Tergicristalli"
    assert created_data["cost"] == 35.0

    # Verifica che la categoria personalizzata appaia nell'elenco categorie dell'utente
    res_cats = client_with_db.get("/api/maintenance/categories", headers=headers)
    assert res_cats.status_code == 200
    assert "Tergicristalli" in res_cats.json()

    # Verifica il filtraggio esatto per categoria custom
    res_filter = client_with_db.get(f"/api/maintenance?expense_type={custom_type}", headers=headers)
    assert res_filter.status_code == 200
    records = res_filter.json()
    assert len(records) == 1
    assert records[0]["expense_type"] == "Tergicristalli"
    assert records[0]["description"] == "Sostituzione spazzole tergicristallo Bosch Aerotwin"



# =============================================================================
# TEST: Scadenze Predittive (Deadlines)
# =============================================================================

def test_get_deadlines_predictive(client_with_db):
    """Verifica il calcolo delle scadenze e della data prevista di raggiungimento chilometri."""
    headers = {"X-User-Id": "user-deadlines"}

    # 1. Registriamo due rifornimenti per definire l'ultimo km noto (50.000) e daily rate
    client_with_db.post("/api/fuel", json={
        "date": "2025-05-01", "total_km": 49000, "price_per_liter": 1.80, "total_cost": 50.0, "liters": 27.78, "is_full_tank": True
    }, headers=headers)
    client_with_db.post("/api/fuel", json={
        "date": "2025-05-11", "total_km": 50000, "price_per_liter": 1.80, "total_cost": 50.0, "liters": 27.78, "is_full_tank": True
    }, headers=headers)
    # Rateo = (50000 - 49000) / 10 gg = 100 km/giorno

    # 2. Registriamo manutenzione con scadenza a 55.000 Km (mancano 5.000 km -> stimati 50 gg)
    client_with_db.post("/api/maintenance", json={
        "date": "2025-05-11",
        "total_km": 50000,
        "expense_type": "Tagliando",
        "cost": 200.0,
        "expiry_km": 55000,
    }, headers=headers)

    res = client_with_db.get("/api/maintenance/deadlines", headers=headers)
    assert res.status_code == 200
    deadlines = res.json()
    assert len(deadlines) == 1
    dl = deadlines[0]
    assert dl["expense_type"] == "Tagliando"
    assert dl["km_left"] == 5000
    assert dl["priority"] == 3  # Regolare (> 1000 km)
    assert dl["status_color"] == "#28a745"
    assert dl["predicted_date"] is not None


# =============================================================================
# TEST: Get by ID, Update, Delete & Tenant Isolation
# =============================================================================

def test_maintenance_crud_and_tenant_isolation(client_with_db):
    """Verifica dettaglio, modifica parziale, cancellazione e isolamento multi-tenant."""
    headers_a = {"X-User-Id": "user-alice"}
    headers_b = {"X-User-Id": "user-bob"}

    # Alice crea un record
    created = client_with_db.post("/api/maintenance", json={
        "date": "2025-06-01",
        "total_km": 70000,
        "expense_type": "Revisione",
        "cost": 79.0,
    }, headers=headers_a).json()
    rec_id = created["id"]

    # Alice legge il record (200)
    assert client_with_db.get(f"/api/maintenance/{rec_id}", headers=headers_a).status_code == 200

    # Bob tenta di leggere il record di Alice (404)
    assert client_with_db.get(f"/api/maintenance/{rec_id}", headers=headers_b).status_code == 404

    # Alice aggiorna il costo
    upd = client_with_db.put(f"/api/maintenance/{rec_id}", json={"cost": 85.0}, headers=headers_a)
    assert upd.status_code == 200
    assert upd.json()["cost"] == 85.0

    # Bob tenta di modificare il record di Alice (404)
    assert client_with_db.put(f"/api/maintenance/{rec_id}", json={"cost": 10.0}, headers=headers_b).status_code == 404

    # Bob tenta di eliminare il record di Alice (404)
    assert client_with_db.delete(f"/api/maintenance/{rec_id}", headers=headers_b).status_code == 404

    # Alice elimina il record (200)
    del_res = client_with_db.delete(f"/api/maintenance/{rec_id}", headers=headers_a)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Verifica che ora sia 404 per tutti
    assert client_with_db.get(f"/api/maintenance/{rec_id}", headers=headers_a).status_code == 404
