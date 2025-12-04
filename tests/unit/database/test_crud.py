from datetime import date
from database import crud

def test_create_refueling(db_session):
    """Verifica persistenza record Rifornimento."""
    # 1. Arrange & Act
    refueling = crud.create_refueling(
        db=db_session,
        date_obj=date(2025, 1, 1),
        total_km=50000,
        price_per_liter=1.80,
        total_cost=90.00,
        liters=50.00,
        is_full_tank=True,
        notes="Test unitario"
    )
    
    # 2. Assert Immediato (Oggetto ritornato)
    assert refueling.id is not None
    assert refueling.total_km == 50000
    
    # 3. Assert Persistenza (Rilettura dal DB)
    saved_records = crud.get_all_refuelings(db_session)
    assert len(saved_records) == 1
    assert saved_records[0].notes == "Test unitario"

def test_create_maintenance(db_session):
    """Verifica persistenza record Manutenzione."""
    # 1. Arrange & Act
    maintenance = crud.create_maintenance(
        db=db_session,
        date_obj=date(2025, 2, 1),
        total_km=51000,
        expense_type="Tires",
        cost=400.00,
        description="Cambio gomme invernali"
    )
    
    # 2. Assert
    assert maintenance.id is not None
    assert maintenance.expense_type == "Tires"
    assert maintenance.cost == 400.00