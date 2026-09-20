"""
Test unitari per il Router Report, Esportazione & Importazione (/api/reports).
Verifica statistiche di export, download Excel e template vuoto, generazione libretto PDF,
anteprima file di importazione (CSV/Excel) e salvataggio transazionale (commit).
"""
# pyrefly: ignore [missing-import]
import io
import pytest
from datetime import date
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

from src.api.server import app
from src.api.deps import get_db
from src.database import crud


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
# TEST: Statistiche di Esportazione
# =============================================================================

def test_export_stats_empty(client_with_db):
    """Verifica che un utente senza dati riceva conteggi a zero."""
    headers = {"X-User-Id": "user-reports-empty"}
    res = client_with_db.get("/api/reports/stats", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["refuelings_count"] == 0
    assert data["maintenances_count"] == 0
    assert data["years_available"] == []


def test_export_stats_with_data(client_with_db, db_session):
    """Verifica il calcolo corretto di rifornimenti, manutenzioni e anni disponibili."""
    headers = {"X-User-Id": "user-reports-stats"}

    crud.create_refueling(
        db_session,
        user_id="user-reports-stats",
        date_obj=date(2025, 5, 10),
        total_km=15000,
        price_per_liter=1.85,
        total_cost=50.0,
        liters=27.0,
        is_full_tank=True,
    )
    crud.create_maintenance(
        db_session,
        user_id="user-reports-stats",
        date_obj=date(2024, 11, 20),
        total_km=10000,
        expense_type="Tagliando",
        cost=250.0,
    )

    res = client_with_db.get("/api/reports/stats", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["refuelings_count"] == 1
    assert data["maintenances_count"] == 1
    assert 2024 in data["years_available"]


# =============================================================================
# TEST: Download Excel e Template
# =============================================================================

def test_download_excel_empty_error(client_with_db):
    """Verifica che l'export Excel sollevi HTTP 400 se l'utente non ha record."""
    headers = {"X-User-Id": "user-excel-empty"}
    res = client_with_db.get("/api/reports/excel", headers=headers)
    assert res.status_code == 400
    assert "Nessun dato presente" in res.json()["detail"]


def test_download_excel_success(client_with_db, db_session):
    """Verifica la generazione corretta del file Excel multi-sheet."""
    headers = {"X-User-Id": "user-excel-success"}

    crud.create_refueling(
        db_session,
        user_id="user-excel-success",
        date_obj=date(2026, 1, 15),
        total_km=20000,
        price_per_liter=1.80,
        total_cost=60.0,
        liters=33.33,
        is_full_tank=True,
    )

    res = client_with_db.get("/api/reports/excel", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "attachment; filename=fuelpytracker_backup_" in res.headers["content-disposition"]
    # Verifica che il contenuto sia un archivio zip valido (formato .xlsx)
    assert res.content.startswith(b"PK")


def test_download_template_success(client_with_db):
    """Verifica il download del modello Excel vuoto pre-formattato."""
    headers = {"X-User-Id": "user-template"}
    res = client_with_db.get("/api/reports/template", headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert "FuelPyTracker_Template.xlsx" in res.headers["content-disposition"]
    assert res.content.startswith(b"PK")


# =============================================================================
# TEST: Generazione Libretto Manutenzione PDF
# =============================================================================

def test_generate_pdf_booklet(client_with_db, db_session):
    """Verifica la compilazione del libretto manutenzione in PDF."""
    headers = {"X-User-Id": "user-pdf-booklet"}

    crud.create_maintenance(
        db_session,
        user_id="user-pdf-booklet",
        date_obj=date(2025, 6, 1),
        total_km=30000,
        expense_type="Tagliando Completo",
        cost=350.0,
        description="Olio, filtro aria, filtro antipolline",
        expiry_km=45000,
        expiry_date=date(2026, 6, 1),
    )

    payload = {
        "owner_name": "Mario Rossi",
        "plate": "FE123XY",
        "car_model": "Volkswagen Golf 8",
        "year": None,
    }

    res = client_with_db.post("/api/reports/pdf", json=payload, headers=headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert "Libretto_Manutenzione_FE123XY_completo.pdf" in res.headers["content-disposition"]
    # Verifica firma magica PDF
    assert res.content.startswith(b"%PDF")


def test_generate_pdf_booklet_filtered_year(client_with_db, db_session):
    """Verifica la generazione PDF filtrata per specifico anno solare."""
    headers = {"X-User-Id": "user-pdf-year"}

    crud.create_maintenance(
        db_session,
        user_id="user-pdf-year",
        date_obj=date(2024, 3, 10),
        total_km=25000,
        expense_type="Cambio Gomme",
        cost=400.0,
    )

    payload = {
        "owner_name": "Anna Bianchi",
        "plate": "AB999ZZ",
        "car_model": "Fiat 500",
        "year": 2024,
    }

    res = client_with_db.post("/api/reports/pdf", json=payload, headers=headers)
    assert res.status_code == 200
    assert "Libretto_Manutenzione_AB999ZZ_2024.pdf" in res.headers["content-disposition"]
    assert res.content.startswith(b"%PDF")


# =============================================================================
# TEST: Anteprima Importazione (Staging)
# =============================================================================

def test_import_preview_invalid_extension(client_with_db):
    """Verifica il rifiuto di formati non supportati (.txt, .json, ecc.)."""
    headers = {"X-User-Id": "user-import-invalid"}
    fake_file = io.BytesIO(b"Hello world")
    response = client_with_db.post(
        "/api/reports/import/preview",
        files={"file": ("test.txt", fake_file, "text/plain")},
        headers=headers,
    )
    assert response.status_code == 400
    assert "Formato non supportato" in response.json()["detail"]


def test_import_preview_valid_csv(client_with_db):
    """Verifica il parsing di un file CSV valido con righe di rifornimento."""
    headers = {"X-User-Id": "user-import-csv"}
    csv_content = (
        "Data,KM,Prezzo,Costo,Litri,Pieno,Note\n"
        "2026-03-01,10000,1.85,50.00,27.03,True,Rifornimento autostrada\n"
        "2026-03-15,10600,1.82,45.50,25.00,True,Rifornimento città\n"
    ).encode("utf-8")

    fake_file = io.BytesIO(csv_content)
    response = client_with_db.post(
        "/api/reports/import/preview",
        files={"file": ("rifornimenti.csv", fake_file, "text/csv")},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["fuel_rows"]) == 2
    assert "Nuovo" in data["fuel_summary"]


# =============================================================================
# TEST: Salvataggio Transazionale Righe Importate (Commit)
# =============================================================================

def test_import_commit_insert_and_update(client_with_db, db_session):
    """Verifica il commit transazionale di righe nuove e aggiornate per carburante e manutenzioni."""
    headers = {"X-User-Id": "user-import-commit"}

    # 1. Crea un record preesistente a DB per testare la modifica
    existing_fuel = crud.create_refueling(
        db_session,
        user_id="user-import-commit",
        date_obj=date(2026, 2, 1),
        total_km=5000,
        price_per_liter=1.75,
        total_cost=35.0,
        liters=20.0,
        is_full_tank=True,
        notes="Nota originale",
    )

    existing_maint = crud.create_maintenance(
        db_session,
        user_id="user-import-commit",
        date_obj=date(2026, 2, 5),
        total_km=5050,
        expense_type="Lavaggio",
        cost=15.0,
        description="Lavaggio esterno",
    )

    # 2. Prepara il payload con 1 nuovo + 1 aggiornamento per entrambi i domini
    commit_payload = {
        "fuel_rows": [
            {
                "status": "Modifica",
                "db_id": existing_fuel.id,
                "date": "2026-02-01",
                "total_km": 5000,
                "price_per_liter": 1.76,
                "total_cost": 35.20,
                "liters": 20.0,
                "is_full_tank": True,
                "notes": "Nota aggiornata via import",
            },
            {
                "status": "Nuovo",
                "db_id": None,
                "date": "2026-02-15",
                "total_km": 5600,
                "price_per_liter": 1.80,
                "total_cost": 54.0,
                "liters": 30.0,
                "is_full_tank": True,
                "notes": "Nuovo rifornimento",
            },
        ],
        "maintenance_rows": [
            {
                "status": "Modifica",
                "db_id": existing_maint.id,
                "date": "2026-02-05",
                "total_km": 5050,
                "expense_type": "Lavaggio Completo",
                "cost": 25.0,
                "description": "Interno ed esterno",
            },
            {
                "status": "Nuovo",
                "db_id": None,
                "date": "2026-02-20",
                "total_km": 5800,
                "expense_type": "Tagliando",
                "cost": 180.0,
                "description": "Cambio olio",
            },
        ],
    }

    res_commit = client_with_db.post(
        "/api/reports/import/commit",
        json=commit_payload,
        headers=headers,
    )
    assert res_commit.status_code == 200
    data = res_commit.json()
    assert data["success"] is True
    assert data["fuel_inserted"] == 1
    assert data["fuel_updated"] == 1
    assert data["maintenance_inserted"] == 1
    assert data["maintenance_updated"] == 1

    # 3. Verifica persistenza effettiva a DB
    fuels = crud.get_all_refuelings(db_session, "user-import-commit")
    assert len(fuels) == 2
    updated_fuel = next(f for f in fuels if f.id == existing_fuel.id)
    assert updated_fuel.notes == "Nota aggiornata via import"
    assert updated_fuel.price_per_liter == 1.76

    maints = crud.get_all_maintenances(db_session, "user-import-commit")
    assert len(maints) == 2
    updated_m = next(m for m in maints if m.id == existing_maint.id)
    assert updated_m.expense_type == "Lavaggio Completo"
    assert updated_m.cost == 25.0
