"""
Test unitari per il Router Fuel di FastAPI (/api/fuel) e la logica di dominio.
Verifica CRUD rifornimenti, calcolo metriche Full-to-Full, validazione pre-flight e scansione OCR.
"""
import io
# pyrefly: ignore [missing-import]
import pytest
from datetime import date
from unittest.mock import patch, MagicMock
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

from src.api.server import app
from src.api.deps import get_db
from src.services.ocr.models import ReceiptData


@pytest.fixture
def client_with_db(db_session):
    """Fixture che inietta una sessione SQLite in memoria isolata nell'app FastAPI."""
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
# TEST: GET /api/fuel & POST /api/fuel
# =============================================================================

def test_get_refuelings_empty(client_with_db):
    """Verifica che un utente senza record riceva una lista vuota."""
    response = client_with_db.get("/api/fuel", headers={"X-User-Id": "user-empty-1"})
    assert response.status_code == 200
    assert response.json() == []


def test_create_refueling_success(client_with_db):
    """Verifica la creazione con successo di un rifornimento valido."""
    payload = {
        "date": "2025-06-01",
        "total_km": 50000,
        "price_per_liter": 1.750,
        "total_cost": 70.0,
        "liters": 40.0,
        "is_full_tank": True,
        "notes": "Eni Station",
    }
    response = client_with_db.post("/api/fuel", json=payload, headers={"X-User-Id": "user-test-1"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["user_id"] == "user-test-1"
    assert data["total_km"] == 50000
    assert data["liters"] == 40.0
    assert data["is_full_tank"] is True
    assert data["notes"] == "Eni Station"
    assert data["delta_km"] == 0
    assert data["km_per_liter"] is None
    assert data["days_since_last"] == 0


def test_create_refueling_validation_pydantic(client_with_db):
    """Verifica che valori negativi o non validi vengano respinti con HTTP 422."""
    invalid_payload = {
        "date": "2025-06-01",
        "total_km": -100,  # Negativo non ammesso
        "price_per_liter": 1.75,
        "total_cost": 70.0,
        "liters": 40.0,
    }
    response = client_with_db.post("/api/fuel", json=invalid_payload, headers={"X-User-Id": "user-test-1"})
    assert response.status_code == 422


def test_create_refueling_chronological_anomaly(client_with_db):
    """Verifica che un'anomalia chilometrica nel tempo venga bloccata con HTTP 400."""
    headers = {"X-User-Id": "user-chrono-1"}
    # Record iniziale: 50.000 km il 10 giugno
    client_with_db.post("/api/fuel", json={
        "date": "2025-06-10",
        "total_km": 50000,
        "price_per_liter": 1.80,
        "total_cost": 50.0,
        "liters": 27.78,
        "is_full_tank": True,
    }, headers=headers)

    # Tentativo di inserimento il 12 giugno con km inferiori (49.000 km)
    response = client_with_db.post("/api/fuel", json={
        "date": "2025-06-12",
        "total_km": 49000,
        "price_per_liter": 1.80,
        "total_cost": 50.0,
        "liters": 27.78,
        "is_full_tank": True,
    }, headers=headers)
    assert response.status_code == 400
    assert "Impossibile scendere di chilometri" in response.json()["detail"]


def test_refueling_full_to_full_calculation(client_with_db):
    """Verifica il calcolo accurato dell'efficienza km/L con algoritmo Full-to-Full."""
    headers = {"X-User-Id": "user-calc-1"}
    
    # 1° Pieno: 10.000 Km il 1° Maggio (ancora di partenza)
    client_with_db.post("/api/fuel", json={
        "date": "2025-05-01",
        "total_km": 10000,
        "price_per_liter": 1.80,
        "total_cost": 90.0,
        "liters": 50.0,
        "is_full_tank": True,
    }, headers=headers)

    # 2° Pieno: 10.600 Km il 10 Maggio con 30 Litri erogati
    # Delta km = 600, Delta giorni = 9, Consumo = 600 / 30 = 20.0 km/L
    res = client_with_db.post("/api/fuel", json={
        "date": "2025-05-10",
        "total_km": 10600,
        "price_per_liter": 1.80,
        "total_cost": 54.0,
        "liters": 30.0,
        "is_full_tank": True,
    }, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["delta_km"] == 600
    assert data["days_since_last"] == 9
    assert data["km_per_liter"] == 20.0


def test_get_refuelings_filter_by_year(client_with_db):
    """Verifica il filtro per anno solare sulla lista rifornimenti."""
    headers = {"X-User-Id": "user-year-filter"}
    
    client_with_db.post("/api/fuel", json={
        "date": "2024-11-20",
        "total_km": 40000,
        "price_per_liter": 1.70,
        "total_cost": 50.0,
        "liters": 29.41,
        "is_full_tank": True,
    }, headers=headers)

    client_with_db.post("/api/fuel", json={
        "date": "2025-03-15",
        "total_km": 45000,
        "price_per_liter": 1.75,
        "total_cost": 60.0,
        "liters": 34.28,
        "is_full_tank": True,
    }, headers=headers)

    # Filtra solo per anno 2025
    res_2025 = client_with_db.get("/api/fuel?year=2025", headers=headers)
    assert res_2025.status_code == 200
    records = res_2025.json()
    assert len(records) == 1
    assert records[0]["date"] == "2025-03-15"

    # Senza filtro recupera entrambi
    res_all = client_with_db.get("/api/fuel", headers=headers)
    assert len(res_all.json()) == 2


# =============================================================================
# TEST: GET, PUT, DELETE per ID e Tenant Isolation
# =============================================================================

def test_get_refueling_by_id(client_with_db):
    """Verifica il recupero di un singolo record per ID."""
    headers = {"X-User-Id": "user-crud-1"}
    created = client_with_db.post("/api/fuel", json={
        "date": "2025-01-10",
        "total_km": 15000,
        "price_per_liter": 1.82,
        "total_cost": 50.0,
        "liters": 27.47,
        "is_full_tank": True,
    }, headers=headers).json()

    rec_id = created["id"]
    response = client_with_db.get(f"/api/fuel/{rec_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == rec_id

    # Record inesistente solleva 404
    missing = client_with_db.get("/api/fuel/999999", headers=headers)
    assert missing.status_code == 404


def test_update_refueling(client_with_db):
    """Verifica l'aggiornamento parziale di un rifornimento."""
    headers = {"X-User-Id": "user-crud-update"}
    created = client_with_db.post("/api/fuel", json={
        "date": "2025-02-01",
        "total_km": 20000,
        "price_per_liter": 1.80,
        "total_cost": 60.0,
        "liters": 33.33,
        "is_full_tank": True,
        "notes": "Prima nota",
    }, headers=headers).json()

    rec_id = created["id"]
    update_res = client_with_db.put(
        f"/api/fuel/{rec_id}",
        json={"notes": "Nota aggiornata con successo", "total_cost": 65.0},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["notes"] == "Nota aggiornata con successo"
    assert update_res.json()["total_cost"] == 65.0


def test_delete_refueling(client_with_db):
    """Verifica l'eliminazione di un rifornimento."""
    headers = {"X-User-Id": "user-crud-delete"}
    created = client_with_db.post("/api/fuel", json={
        "date": "2025-02-15",
        "total_km": 22000,
        "price_per_liter": 1.79,
        "total_cost": 45.0,
        "liters": 25.14,
        "is_full_tank": True,
    }, headers=headers).json()

    rec_id = created["id"]
    del_res = client_with_db.delete(f"/api/fuel/{rec_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Verifica che ora restituisca 404
    get_res = client_with_db.get(f"/api/fuel/{rec_id}", headers=headers)
    assert get_res.status_code == 404


def test_tenant_isolation(client_with_db):
    """Verifica l'isolamento multi-tenant: l'utente B non può vedere o modificare dati dell'utente A."""
    headers_a = {"X-User-Id": "user-alpha"}
    headers_b = {"X-User-Id": "user-beta"}

    created_a = client_with_db.post("/api/fuel", json={
        "date": "2025-04-01",
        "total_km": 30000,
        "price_per_liter": 1.85,
        "total_cost": 80.0,
        "liters": 43.24,
        "is_full_tank": True,
    }, headers=headers_a).json()

    rec_id = created_a["id"]

    # Utente B tenta di accedere al record di A -> 404
    assert client_with_db.get(f"/api/fuel/{rec_id}", headers=headers_b).status_code == 404

    # Utente B tenta di modificare il record di A -> 404
    assert client_with_db.put(f"/api/fuel/{rec_id}", json={"notes": "Hacked"}, headers=headers_b).status_code == 404

    # Utente B tenta di cancellare il record di A -> 404
    assert client_with_db.delete(f"/api/fuel/{rec_id}", headers=headers_b).status_code == 404


# =============================================================================
# TEST: POST /api/fuel/validate (Pre-flight check)
# =============================================================================

def test_validate_refueling_preflight(client_with_db):
    """Verifica il funzionamento dell'endpoint di validazione pre-flight."""
    headers = {"X-User-Id": "user-preflight"}

    client_with_db.post("/api/fuel", json={
        "date": "2025-07-01",
        "total_km": 60000,
        "price_per_liter": 1.80,
        "total_cost": 60.0,
        "liters": 33.33,
        "is_full_tank": True,
    }, headers=headers)

    # Validazione coerente
    valid_res = client_with_db.post("/api/fuel/validate", json={
        "date": "2025-07-15",
        "km": 60800,
        "price": 1.82,
        "cost": 50.0,
        "is_full": True,
    }, headers=headers)
    assert valid_res.status_code == 200
    val_data = valid_res.json()
    assert val_data["is_valid"] is True
    assert val_data["prev_km"] == 60000

    # Validazione incoerente (km inferiori nel futuro)
    invalid_res = client_with_db.post("/api/fuel/validate", json={
        "date": "2025-07-15",
        "km": 59000,
        "price": 1.82,
        "cost": 50.0,
        "is_full": True,
    }, headers=headers)
    assert invalid_res.status_code == 200
    assert invalid_res.json()["is_valid"] is False


# =============================================================================
# TEST: POST /api/fuel/ocr (Receipt Parsing)
# =============================================================================

def test_ocr_non_image_upload(client_with_db):
    """Verifica che il caricamento di file non-immagine venga rifiutato con HTTP 400."""
    fake_file = io.BytesIO(b"Questo e un semplice file di testo, non uno scontrino.")
    response = client_with_db.post(
        "/api/fuel/ocr",
        files={"file": ("test.txt", fake_file, "text/plain")},
    )
    assert response.status_code == 400
    assert "immagine valida" in response.json()["detail"]


def test_ocr_demo_mode(client_with_db):
    """Verifica che in modalità Demo l'OCR restituisca dati simulati senza chiamare OpenAI."""
    with patch("src.services.ocr.engine.is_demo_mode", return_value=True):
        fake_image = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00")
        response = client_with_db.post(
            "/api/fuel/ocr",
            files={"file": ("scontrino.jpg", fake_image, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_cost"] == 68.50
        assert data["price_per_liter"] == 1.869
        assert data["station_name"] == "Eni Station Demo"


def test_ocr_mocked_ai_success(client_with_db):
    """Verifica il parsing OCR simulando la risposta di successo del modello AI."""
    mock_rd = ReceiptData()
    mock_rd.total_cost = 55.40
    mock_rd.price_per_liter = 1.789
    mock_rd.liters = 30.97
    mock_rd.date = date(2025, 8, 14)
    mock_rd.station_name = "Q8 Easy"
    mock_rd.raw_text = "Analisi GPT-4o Completata"

    with patch("src.api.routers.fuel.analyze_receipt", return_value=mock_rd):
        fake_image = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
        response = client_with_db.post(
            "/api/fuel/ocr",
            files={"file": ("scontrino.png", fake_image, "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_cost"] == 55.40
        assert data["price_per_liter"] == 1.789
        assert data["station_name"] == "Q8 Easy"
        assert data["date"] == "2025-08-14"


def test_ocr_status_endpoint(client_with_db):
    """Verifica che l'endpoint GET /api/fuel/ocr/status risponda correttamente."""
    response = client_with_db.get("/api/fuel/ocr/status")
    assert response.status_code == 200
    data = response.json()
    assert "available" in data
    assert "is_demo" in data
    assert "message" in data


def test_ocr_missing_key_returns_failure(client_with_db):
    """Verifica che quando l'API key manca, l'OCR restituisca success=False con messaggio chiaro."""
    mock_rd = ReceiptData()
    mock_rd.raw_text = "ERRORE: API Key OpenAI mancante in backend/.env o variabili d'ambiente."

    with patch("src.api.routers.fuel.analyze_receipt", return_value=mock_rd):
        fake_image = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
        response = client_with_db.post(
            "/api/fuel/ocr",
            files={"file": ("scontrino.png", fake_image, "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "ERRORE" in data["raw_text"]
