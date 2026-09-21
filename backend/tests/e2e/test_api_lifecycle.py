"""
Test End-to-End (E2E) per il Ciclo di Vita Completo delle API V2.0 (/api/*).
Simula programmaticamente l'intero percorso di un client (es. React SPA):
- Health check & validazione schema OpenAPI
- Autenticazione e profilazione utente (/me)
- Configurazione impostazioni personali e categorie dinamiche
- Ciclo carburante completo: validazione pre-flight, algoritmo Full-to-Full e OCR Vision
- Cruscotto analitico Dashboard: KPI aggregati, serie storiche grafici e simulatore viaggi
- Registro officina: spese manutenzione, scadenze predittive semaforiche e routine "Mark as Done"
- Hub report: statistiche, download template/Excel, generazione Libretto PDF e pipeline importazione a due fasi
"""
import io
# pyrefly: ignore [missing-import]
import pytest
from datetime import date
from unittest.mock import patch
# pyrefly: ignore [missing-import]
from fastapi.testclient import TestClient

from src.api.server import app
from src.api.deps import get_db
from src.api.config import DEMO_USER_ID, DEMO_USER_EMAIL


@pytest.fixture
def client_with_db(db_session):
    """Inietta la sessione di database isolata nell'applicazione FastAPI."""
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
# 1. TEST: System Health, Root Redirect & Validazione Specifica OpenAPI
# =============================================================================

def test_system_health_and_openapi_spec(client_with_db):
    """Verifica che il server risponda su /health, reindirizzi su /docs e contenga tutti i 25+ percorsi API."""
    # 1. Health check
    res_health = client_with_db.get("/health")
    assert res_health.status_code == 200
    health_data = res_health.json()
    assert health_data["status"] == "ok"
    assert "version" in health_data
    assert "timestamp" in health_data

    # 2. Redirect root verso Swagger
    res_root = client_with_db.get("/", follow_redirects=False)
    assert res_root.status_code in (307, 302, 301)
    assert res_root.headers["location"] == "/docs"

    # 3. Validazione Specifica OpenAPI
    res_openapi = client_with_db.get("/openapi.json")
    assert res_openapi.status_code == 200
    schema = res_openapi.json()
    assert "paths" in schema
    paths = schema["paths"]

    # Verifica la presenza di tutti i macro-domini registrati
    expected_endpoints = [
        "/health",
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/logout",
        "/api/auth/me",
        "/api/fuel",
        "/api/fuel/validate",
        "/api/fuel/ocr",
        "/api/dashboard/summary",
        "/api/dashboard/charts",
        "/api/dashboard/trip-calculator",
        "/api/maintenance",
        "/api/maintenance/deadlines",
        "/api/reminders",
        "/api/reminders/history",
        "/api/settings",
        "/api/settings/reminder-categories",
        "/api/settings/maintenance-categories",
        "/api/reports/stats",
        "/api/reports/excel",
        "/api/reports/template",
        "/api/reports/pdf",
        "/api/reports/import/preview",
        "/api/reports/import/commit",
    ]
    for ep in expected_endpoints:
        assert ep in paths, f"Endpoint atteso non trovato nello schema OpenAPI: {ep}"


# =============================================================================
# 2. TEST: Ciclo di Vita Completo dell'Utente (End-to-End User Journey)
# =============================================================================

def test_complete_user_lifecycle(client_with_db):
    """
    Esegue in sequenza tutte le operazioni di un utente reale:
    1. Auth (login/register/me)
    2. Settings & Categorie Custom
    3. Rifornimenti (Full-to-Full + OCR)
    4. Dashboard (KPI, grafici, preventivo viaggi)
    5. Manutenzioni & Promemoria (Mark-as-done)
    6. Export e Staging Importazione
    """
    user_id = "user-e2e-complete"
    headers = {"X-User-Id": user_id}

    # -------------------------------------------------------------------------
    # FASE A: Autenticazione & Profilo
    # -------------------------------------------------------------------------
    with patch("src.api.routers.auth.is_demo_mode", return_value=True):
        login_res = client_with_db.post("/api/auth/login", json={
            "email": DEMO_USER_EMAIL,
            "password": "demo_password",
        })
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

    me_res = client_with_db.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["id"] == user_id

    # -------------------------------------------------------------------------
    # FASE B: Preferenze & Categorie Personalizzate
    # -------------------------------------------------------------------------
    # 1. Recupero impostazioni di default auto-provisioning
    sett_res = client_with_db.get("/api/settings", headers=headers)
    assert sett_res.status_code == 200
    sett_data = sett_res.json()
    assert sett_data["price_fluctuation_cents"] == 0.15
    assert sett_data["max_total_cost"] == 120.0

    # 2. Aggiornamento impostazioni
    put_sett = client_with_db.put("/api/settings", json={
        "max_total_cost": 140.0,
        "price_fluctuation_cents": 0.20,
    }, headers=headers)
    assert put_sett.status_code == 200
    assert put_sett.json()["max_total_cost"] == 140.0
    assert put_sett.json()["price_fluctuation_cents"] == 0.20

    # 3. Aggiunta categorie dinamiche
    add_rem_cat = client_with_db.post(
        "/api/settings/reminder-categories",
        json={"category": "Controllo Candele"},
        headers=headers,
    )
    assert add_rem_cat.status_code == 200
    assert "Controllo Candele" in add_rem_cat.json()["reminder_types"]

    add_mai_cat = client_with_db.post(
        "/api/settings/maintenance-categories",
        json={"category": "Cinghia Servizi"},
        headers=headers,
    )
    assert add_mai_cat.status_code == 200
    assert "Cinghia Servizi" in add_mai_cat.json()["maintenance_types"]

    # -------------------------------------------------------------------------
    # FASE C: Rifornimenti (Validazione, Algoritmo Full-to-Full & OCR)
    # -------------------------------------------------------------------------
    # 1. Pre-flight validation
    val_res = client_with_db.post("/api/fuel/validate", json={
        "date": "2026-01-10",
        "km": 10000,
        "price": 1.80,
        "cost": 54.0,
        "is_full": True,
    }, headers=headers)
    assert val_res.status_code == 200
    assert val_res.json()["is_valid"] is True

    # 2. Rifornimento 1: Primo pieno (Base di calcolo, consumo ancora None)
    f1_res = client_with_db.post("/api/fuel", json={
        "date": "2026-01-10",
        "total_km": 10000,
        "price_per_liter": 1.80,
        "total_cost": 54.0,
        "liters": 30.0,
        "is_full_tank": True,
        "notes": "Pieno iniziale di partenza",
    }, headers=headers)
    assert f1_res.status_code == 201

    # 3. Rifornimento 2: Parziale intermedio
    f2_res = client_with_db.post("/api/fuel", json={
        "date": "2026-01-20",
        "total_km": 10300,
        "price_per_liter": 1.82,
        "total_cost": 27.30,
        "liters": 15.0,
        "is_full_tank": False,
        "notes": "Rabbocco parziale autostrada",
    }, headers=headers)
    assert f2_res.status_code == 201

    # 4. Rifornimento 3: Secondo pieno (Trigger del calcolo Full-to-Full)
    # Delta km: 10800 - 10000 = 800 km
    # Litri consumati nel ciclo: 15.0 (parziale) + 25.0 (chiusura pieno) = 40.0 L
    # Consumo reale: 800 / 40 = 20.0 km/L
    f3_res = client_with_db.post("/api/fuel", json={
        "date": "2026-02-01",
        "total_km": 10800,
        "price_per_liter": 1.85,
        "total_cost": 46.25,
        "liters": 25.0,
        "is_full_tank": True,
        "notes": "Secondo pieno con chiusura ciclo",
    }, headers=headers)
    assert f3_res.status_code == 201

    # 5. Verifica elenco rifornimenti con consumi calcolati in real-time
    fuels_list_res = client_with_db.get("/api/fuel", headers=headers)
    assert fuels_list_res.status_code == 200
    fuels_list = fuels_list_res.json()
    assert len(fuels_list) == 3
    # I rifornimenti sono ordinati per data decrescente (il più recente per primo)
    latest_fuel = fuels_list[0]
    assert latest_fuel["total_km"] == 10800
    assert latest_fuel["delta_km"] == 500
    assert latest_fuel["km_per_liter"] == 20.0

    # 6. Test OCR Scontrino (modalità Demo / simulazione fallback)
    with patch("src.services.ocr.engine.is_demo_mode", return_value=True):
        fake_receipt = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00")
        ocr_res = client_with_db.post(
            "/api/fuel/ocr",
            files={"file": ("scontrino_test.jpg", fake_receipt, "image/jpeg")},
            headers=headers,
        )
        assert ocr_res.status_code == 200
        ocr_data = ocr_res.json()
        assert ocr_data["success"] is True
        assert ocr_data["total_cost"] == 68.50
        assert ocr_data["price_per_liter"] == 1.869

    # -------------------------------------------------------------------------
    # FASE D: Dashboard, Grafici & Simulatore Viaggi
    # -------------------------------------------------------------------------
    # 1. Cruscotto KPI di Sintesi
    dash_res = client_with_db.get("/api/dashboard/summary", headers=headers)
    assert dash_res.status_code == 200
    dash_kpi = dash_res.json()
    # Spesa totale carburante: 54.0 + 27.30 + 46.25 = 127.55
    assert dash_kpi["total_fuel_cost"] == pytest.approx(127.55, 0.01)
    assert dash_kpi["avg_km_per_liter"] == 20.0
    assert dash_kpi["last_refueling"]["total_cost"] == 46.25
    assert 0 <= dash_kpi["health_score"]["score"] <= 100

    # 2. Serie Temporali per Grafici
    charts_res = client_with_db.get("/api/dashboard/charts?time_range=1y", headers=headers)
    assert charts_res.status_code == 200
    charts_data = charts_res.json()
    assert "price_trend" in charts_data
    assert "efficiency" in charts_data
    assert "monthly_spending" in charts_data
    assert len(charts_data["price_trend"]) == 3

    # 4. Simulatore Costi di Viaggio (500 km con consumo reale 20 km/l e prezzo medio ~1.82 €/L)
    trip_res = client_with_db.post("/api/dashboard/trip-calculator", json={
        "trip_km": 500.0,
    }, headers=headers)
    assert trip_res.status_code == 200
    trip_data = trip_res.json()
    assert trip_data["trip_km"] == 500.0
    assert trip_data["liters_needed"] == 25.0  # 500 / 20 = 25 litri
    assert trip_data["estimated_cost"] > 0
    assert trip_data["cost_per_km"] > 0

    # -------------------------------------------------------------------------
    # FASE E: Manutenzioni, Scadenze Predittive & Promemoria (Mark as Done)
    # -------------------------------------------------------------------------
    # 1. Creazione Intervento Officina
    maint_res = client_with_db.post("/api/maintenance", json={
        "date": "2026-01-25",
        "total_km": 10500,
        "expense_type": "Tagliando Completo",
        "cost": 280.0,
        "description": "Olio, filtro olio, filtro aria e controllo freni",
        "expiry_km": 25500,
        "expiry_date": "2027-01-25",
    }, headers=headers)
    assert maint_res.status_code == 201
    maint_id = maint_res.json()["id"]

    # 2. Scadenze Predittive
    deadlines_res = client_with_db.get("/api/maintenance/deadlines", headers=headers)
    assert deadlines_res.status_code == 200
    deadlines = deadlines_res.json()
    target_dl = next((d for d in deadlines if d["id"] == maint_id), None)
    assert target_dl is not None
    assert target_dl["km_left"] == 25500 - 10800  # 14700 km residui
    assert target_dl["priority"] in (1, 2, 3)
    assert target_dl["status_color"].startswith("#")

    # 3. Creazione Promemoria Periodico (controllo ogni 5000 km, km attuali 10800 -> target 15800)
    rem_res = client_with_db.post("/api/reminders", json={
        "title": "Controllo Pressione Gomme",
        "frequency_km": 5000,
        "current_km": 10800,
        "notes": "Pressione a 2.3 bar anteriori e 2.2 posteriori",
    }, headers=headers)
    assert rem_res.status_code == 201
    rem_id = rem_res.json()["id"]
    assert rem_res.json()["target_km"] == 15800
    assert rem_res.json()["progress"] == 0.0

    # 4. Esecuzione Azione "Mark as Done" del promemoria
    comp_res = client_with_db.post(f"/api/reminders/{rem_id}/complete", json={
        "check_date": "2026-02-05",
        "check_km": 11000,
        "notes": "Pressione verificata e regolata",
    }, headers=headers)
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    # Il ciclo si resetta con target 11000 + 5000 = 16000
    assert comp_data["last_km_check"] == 11000
    assert comp_data["target_km"] == 16000

    # 5. Verifica Storico Esecuzioni
    hist_res = client_with_db.get("/api/reminders/history", headers=headers)
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 1
    assert history[0]["reminder_id"] == rem_id
    assert history[0]["km_checked"] == 11000
    assert history[0]["notes"] == "Pressione verificata e regolata"

    # -------------------------------------------------------------------------
    # FASE F: Reports, Esportazioni & Pipeline Importazione a Due Fasi
    # -------------------------------------------------------------------------
    # 1. Statistiche archivio
    stats_res = client_with_db.get("/api/reports/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["refuelings_count"] == 3
    assert stats["maintenances_count"] == 1
    assert 2026 in stats["years_available"]

    # 2. Download Modello Excel vuoto
    tpl_res = client_with_db.get("/api/reports/template", headers=headers)
    assert tpl_res.status_code == 200
    assert tpl_res.content.startswith(b"PK")
    assert "FuelPyTracker_Template.xlsx" in tpl_res.headers["content-disposition"]

    # 3. Download Backup Excel completo
    excel_res = client_with_db.get("/api/reports/excel", headers=headers)
    assert excel_res.status_code == 200
    assert excel_res.content.startswith(b"PK")
    assert "fuelpytracker_backup_" in excel_res.headers["content-disposition"]

    # 4. Generazione Libretto Manutenzione Digitale in PDF
    pdf_res = client_with_db.post("/api/reports/pdf", json={
        "owner_name": "Mario Rossi",
        "plate": "GA123XX",
        "car_model": "Fiat Punto 1.2",
        "year": 2026,
    }, headers=headers)
    assert pdf_res.status_code == 200
    assert pdf_res.content.startswith(b"%PDF")
    assert "Libretto_Manutenzione_GA123XX_2026.pdf" in pdf_res.headers["content-disposition"]

    # 5. Pipeline di Importazione a Due Fasi: Anteprima (Staging Preview)
    csv_import = (
        "Data,KM,Prezzo,Costo,Litri,Pieno,Note\n"
        "2026-02-10,11400,1.79,35.80,20.0,True,Rifornimento extra da import\n"
    ).encode("utf-8")
    preview_res = client_with_db.post(
        "/api/reports/import/preview",
        files={"file": ("import_test.csv", io.BytesIO(csv_import), "text/csv")},
        headers=headers,
    )
    assert preview_res.status_code == 200
    preview_data = preview_res.json()
    assert preview_data["success"] is True
    assert len(preview_data["fuel_rows"]) == 1
    assert "Nuovo" in preview_data["fuel_summary"]

    # 6. Pipeline di Importazione: Commit Transazionale
    commit_res = client_with_db.post("/api/reports/import/commit", json={
        "fuel_rows": [
            {
                "status": "Nuovo",
                "db_id": None,
                "date": "2026-02-10",
                "total_km": 11400,
                "price_per_liter": 1.79,
                "total_cost": 35.80,
                "liters": 20.0,
                "is_full_tank": True,
                "notes": "Rifornimento confermato da importazione E2E",
            }
        ],
        "maintenance_rows": [],
    }, headers=headers)
    assert commit_res.status_code == 200
    assert commit_res.json()["success"] is True
    assert commit_res.json()["fuel_inserted"] == 1

    # 7. Verifica finale dell'incremento record su tabella fuel
    final_fuels_res = client_with_db.get("/api/fuel", headers=headers)
    assert final_fuels_res.status_code == 200
    assert len(final_fuels_res.json()) == 4
