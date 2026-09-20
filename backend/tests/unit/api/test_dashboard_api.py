"""
Test unitari per il Router Dashboard & Analytics di FastAPI (/api/dashboard).
Verifica KPI aggregati, Car Health Score, aggregazione serie grafici e simulatore Trip Calculator.
"""
# pyrefly: ignore [missing-import]
import pytest
from datetime import date, timedelta
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
# TEST: GET /api/dashboard/summary
# =============================================================================

def test_dashboard_summary_empty(client_with_db):
    """Verifica che un utente senza record riceva un summary coerente e default 100% health."""
    headers = {"X-User-Id": "user-dash-empty"}
    response = client_with_db.get("/api/dashboard/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["current_km"] == 0
    assert data["last_refueling"] is None
    assert data["total_fuel_cost"] == 0.0
    assert data["total_maintenance_cost"] == 0.0
    assert data["total_spent"] == 0.0
    assert data["avg_km_per_liter"] == 0.0
    assert data["health_score"]["score"] == 100
    assert data["health_score"]["status_color"] == "green"
    assert data["partial_alert"]["is_warning"] is False


def test_dashboard_summary_populated(client_with_db):
    """Verifica il calcolo corretto di tutti i KPI in presenza di rifornimenti e manutenzioni."""
    headers = {"X-User-Id": "user-dash-full"}

    # 1. Rifornimenti
    client_with_db.post("/api/fuel", json={
        "date": "2025-05-01", "total_km": 10000, "price_per_liter": 1.80, "total_cost": 90.0, "liters": 50.0, "is_full_tank": True
    }, headers=headers)
    client_with_db.post("/api/fuel", json={
        "date": "2025-05-10", "total_km": 10500, "price_per_liter": 1.80, "total_cost": 45.0, "liters": 25.0, "is_full_tank": True
    }, headers=headers)

    # 2. Manutenzione
    client_with_db.post("/api/maintenance", json={
        "date": "2025-05-05", "total_km": 10200, "expense_type": "Gomme", "cost": 300.0
    }, headers=headers)

    response = client_with_db.get("/api/dashboard/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["current_km"] == 10500
    assert data["last_refueling"]["total_cost"] == 45.0
    assert data["total_fuel_cost"] == 135.0  # 90 + 45
    assert data["total_maintenance_cost"] == 300.0
    assert data["total_spent"] == 435.0
    assert data["avg_km_per_liter"] == 20.0  # (10500 - 10000) / 25


def test_dashboard_health_score_penalty(client_with_db):
    """Verifica che scadenze superate applichino il giusto malus al Car Health Score."""
    headers = {"X-User-Id": "user-dash-health"}

    # Rifornimento: auto a 60.000 Km
    client_with_db.post("/api/fuel", json={
        "date": "2025-06-01", "total_km": 60000, "price_per_liter": 1.80, "total_cost": 50.0, "liters": 27.78, "is_full_tank": True
    }, headers=headers)

    # Manutenzione scaduta a 58.000 Km (malus -20)
    client_with_db.post("/api/maintenance", json={
        "date": "2025-01-01", "total_km": 40000, "expense_type": "Tagliando", "cost": 200.0, "expiry_km": 58000
    }, headers=headers)

    response = client_with_db.get("/api/dashboard/summary", headers=headers)
    assert response.status_code == 200
    score_info = response.json()["health_score"]
    assert score_info["score"] <= 80
    assert len(score_info["issues"]) > 0


# =============================================================================
# TEST: GET /api/dashboard/charts
# =============================================================================

def test_dashboard_charts(client_with_db):
    """Verifica l'erogazione delle serie temporali per i grafici analitici."""
    headers = {"X-User-Id": "user-dash-charts"}

    client_with_db.post("/api/fuel", json={
        "date": "2025-03-01", "total_km": 10000, "price_per_liter": 1.75, "total_cost": 70.0, "liters": 40.0, "is_full_tank": True
    }, headers=headers)
    client_with_db.post("/api/fuel", json={
        "date": "2025-03-15", "total_km": 10600, "price_per_liter": 1.80, "total_cost": 54.0, "liters": 30.0, "is_full_tank": True
    }, headers=headers)
    client_with_db.post("/api/maintenance", json={
        "date": "2025-03-10", "total_km": 10300, "expense_type": "Filtro", "cost": 50.0
    }, headers=headers)

    response = client_with_db.get("/api/dashboard/charts?time_range=all", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["price_trend"]) == 2
    assert len(data["efficiency"]) == 1
    assert data["efficiency"][0]["km_per_liter"] == 20.0
    assert len(data["monthly_spending"]) == 1
    month_point = data["monthly_spending"][0]
    assert month_point["month"] == "2025-03"
    assert month_point["fuel_cost"] == 124.0
    assert month_point["maintenance_cost"] == 50.0
    assert month_point["total_cost"] == 174.0


# =============================================================================
# TEST: POST /api/dashboard/trip-calculator
# =============================================================================

def test_trip_calculator(client_with_db):
    """Verifica il calcolo preventivo del costo di viaggio con valori personalizzati e fallback."""
    headers = {"X-User-Id": "user-dash-calc"}

    # Con parametri espliciti: 200 Km a 20 Km/L con prezzo 1.80 €/L -> 10 L -> 18.00 €
    response = client_with_db.post("/api/dashboard/trip-calculator", json={
        "trip_km": 200,
        "avg_kml": 20.0,
        "fuel_price": 1.80,
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["trip_km"] == 200.0
    assert data["liters_needed"] == 10.0
    assert data["estimated_cost"] == 18.0
    assert data["cost_per_km"] == 0.09

    # Con fallback su default storici (senza errori)
    fallback_res = client_with_db.post("/api/dashboard/trip-calculator", json={
        "trip_km": 100,
    }, headers=headers)
    assert fallback_res.status_code == 200
    assert fallback_res.json()["estimated_cost"] > 0
