from datetime import date
from database import crud

def test_create_refueling(db_session):
    """
    Verifica che un rifornimento venga inserito correttamente nel DB.
    """
    # Arrange (Preparazione dati)
    test_date = date(2025, 1, 1)
    km = 50000
    price = 1.80
    cost = 90.00
    liters = 50.00
    
    # Act (Esecuzione)
    refueling = crud.create_refueling(
        db=db_session,
        date_obj=test_date,
        total_km=km,
        price_per_liter=price,
        total_cost=cost,
        liters=liters,
        is_full_tank=True,
        notes="Test unitario"
    )
    
    # Assert (Verifica risultati)
    assert refueling.id is not None
    assert refueling.total_km == 50000
    assert refueling.total_cost == 90.00
    
    # Verifica che sia stato effettivamente salvato nel DB
    saved_records = crud.get_all_refuelings(db_session)
    assert len(saved_records) == 1
    assert saved_records[0].notes == "Test unitario"

def test_create_maintenance(db_session):
    """
    Verifica inserimento manutenzione.
    """
    maintenance = crud.create_maintenance(
        db=db_session,
        date_obj=date(2025, 2, 1),
        total_km=51000,
        expense_type="Tires",
        cost=400.00,
        description="Cambio gomme invernali"
    )
    
    assert maintenance.id is not None
    assert maintenance.expense_type == "Tires"
    assert maintenance.cost == 400.00