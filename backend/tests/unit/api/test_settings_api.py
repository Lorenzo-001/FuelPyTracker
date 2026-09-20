"""
Test unitari per il Router Impostazioni di FastAPI (/api/settings).
Verifica recupero impostazioni predefinite, aggiornamento parametri,
gestione categorie personalizzate (promemoria e manutenzioni) e isolamento multi-tenant.
"""
# pyrefly: ignore [missing-import]
import pytest
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
# TEST: Recupero e Aggiornamento Impostazioni
# =============================================================================

def test_get_default_settings(client_with_db):
    """Verifica che un nuovo utente ottenga le impostazioni di default auto-provisioning."""
    headers = {"X-User-Id": "user-settings-default"}
    response = client_with_db.get("/api/settings", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["price_fluctuation_cents"] == 0.15
    assert data["max_total_cost"] == 120.0
    assert data["max_accumulated_partial_cost"] == 80.0
    assert data["import_kml_min"] == 3.0
    assert data["import_kml_max"] == 30.0
    assert data["import_kml_error"] == 50.0
    assert data["import_kmd_max"] == 1000.0
    assert data["ocr_add_station_to_notes"] is True
    assert data["ocr_add_liters_to_notes"] is True
    assert isinstance(data["reminder_types"], list)
    assert len(data["reminder_types"]) > 0
    assert isinstance(data["maintenance_types"], list)
    assert len(data["maintenance_types"]) > 0


def test_update_settings_partial_and_full(client_with_db):
    """Verifica l'aggiornamento parziale e completo dei parametri applicativi."""
    headers = {"X-User-Id": "user-settings-update"}

    # 1. Aggiornamento parziale soglie
    res_partial = client_with_db.put(
        "/api/settings",
        json={
            "price_fluctuation_cents": 0.25,
            "max_total_cost": 220.0,
            "ocr_add_station_to_notes": False,
        },
        headers=headers,
    )
    assert res_partial.status_code == 200
    data = res_partial.json()
    assert data["price_fluctuation_cents"] == 0.25
    assert data["max_total_cost"] == 220.0
    assert data["ocr_add_station_to_notes"] is False
    # I valori non modificati restano quelli di default
    assert data["max_accumulated_partial_cost"] == 80.0

    # 2. Aggiornamento tolleranze importazione
    res_kml = client_with_db.put(
        "/api/settings",
        json={
            "import_kml_min": 7.5,
            "import_kml_max": 35.0,
            "import_kmd_max": 2000.0,
        },
        headers=headers,
    )
    assert res_kml.status_code == 200
    data2 = res_kml.json()
    assert data2["import_kml_min"] == 7.5
    assert data2["import_kml_max"] == 35.0
    assert data2["import_kmd_max"] == 2000.0
    assert data2["price_fluctuation_cents"] == 0.25


# =============================================================================
# TEST: Gestione Categorie Promemoria
# =============================================================================

def test_reminder_categories_crud(client_with_db):
    """Verifica l'aggiunta e la rimozione di categorie personalizzate per i promemoria."""
    headers = {"X-User-Id": "user-rem-categories"}

    # 1. Aggiungi nuova categoria
    res_add = client_with_db.post(
        "/api/settings/reminder-categories",
        json={"category": "Revisione Bombole Metano"},
        headers=headers,
    )
    assert res_add.status_code == 200
    cats = res_add.json()["reminder_types"]
    assert "Revisione Bombole Metano" in cats

    # 2. Rifiuta duplicati
    res_dup = client_with_db.post(
        "/api/settings/reminder-categories",
        json={"category": "Revisione Bombole Metano"},
        headers=headers,
    )
    assert res_dup.status_code == 400
    assert "già presente" in res_dup.json()["detail"]

    # 3. Elimina la categoria creata
    res_del = client_with_db.delete(
        "/api/settings/reminder-categories/Revisione Bombole Metano",
        headers=headers,
    )
    assert res_del.status_code == 200
    assert "Revisione Bombole Metano" not in res_del.json()["reminder_types"]

    # 4. Errore 404 se si tenta di eliminare una categoria inesistente
    res_del_404 = client_with_db.delete(
        "/api/settings/reminder-categories/CategoriaInesistente",
        headers=headers,
    )
    assert res_del_404.status_code == 404


# =============================================================================
# TEST: Gestione Categorie Manutenzioni
# =============================================================================

def test_maintenance_categories_crud(client_with_db):
    """Verifica l'aggiunta e la rimozione di categorie personalizzate per le manutenzioni."""
    headers = {"X-User-Id": "user-maint-categories"}

    # 1. Aggiungi nuova tipologia
    res_add = client_with_db.post(
        "/api/settings/maintenance-categories",
        json={"category": "Sostituzione Iniettori"},
        headers=headers,
    )
    assert res_add.status_code == 200
    cats = res_add.json()["maintenance_types"]
    assert "Sostituzione Iniettori" in cats

    # 2. Rifiuta duplicati
    res_dup = client_with_db.post(
        "/api/settings/maintenance-categories",
        json={"category": "Sostituzione Iniettori"},
        headers=headers,
    )
    assert res_dup.status_code == 400
    assert "già presente" in res_dup.json()["detail"]

    # 3. Elimina la categoria creata
    res_del = client_with_db.delete(
        "/api/settings/maintenance-categories/Sostituzione Iniettori",
        headers=headers,
    )
    assert res_del.status_code == 200
    assert "Sostituzione Iniettori" not in res_del.json()["maintenance_types"]

    # 4. Errore 404 se si tenta di eliminare una categoria inesistente
    res_del_404 = client_with_db.delete(
        "/api/settings/maintenance-categories/TipologiaInesistente",
        headers=headers,
    )
    assert res_del_404.status_code == 404


# =============================================================================
# TEST: Multi-tenant Isolation
# =============================================================================

def test_settings_multi_tenant_isolation(client_with_db):
    """Verifica che le modifiche apportate da un utente non impattino altri utenti."""
    user_a = {"X-User-Id": "tenant-user-a"}
    user_b = {"X-User-Id": "tenant-user-b"}

    # User A modifica la soglia di fluttuazione
    client_with_db.put(
        "/api/settings",
        json={"price_fluctuation_cents": 0.42},
        headers=user_a,
    )

    # User B legge le sue impostazioni (dovrebbero essere ancora quelle di default)
    res_b = client_with_db.get("/api/settings", headers=user_b)
    assert res_b.status_code == 200
    assert res_b.json()["price_fluctuation_cents"] == 0.15
