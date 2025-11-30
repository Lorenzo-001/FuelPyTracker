from sqlalchemy.orm import Session
from src.database.models import Refueling, Maintenance
from datetime import date
from typing import List, Optional

def create_refueling(
    db: Session, 
    date_obj: date, 
    total_km: int, 
    price_per_liter: float, 
    total_cost: float, 
    liters: float, 
    is_full_tank: bool, 
    notes: Optional[str] = None
) -> Refueling:
    """
    Inserisce un nuovo record di rifornimento nel database.
    """
    new_refueling = Refueling(
        date=date_obj,
        total_km=total_km,
        price_per_liter=price_per_liter,
        total_cost=total_cost,
        liters=liters,
        is_full_tank=is_full_tank,
        notes=notes
    )
    
    db.add(new_refueling)
    db.commit()
    # refresh ricarica l'oggetto dal DB assicurandosi che abbia l'ID generato
    db.refresh(new_refueling)
    return new_refueling

def get_all_refuelings(db: Session) -> List[Refueling]:
    """
    Recupera tutti i rifornimenti ordinati per data decrescente.
    """
    return db.query(Refueling).order_by(Refueling.date.desc()).all()

def create_maintenance(
    db: Session,
    date_obj: date,
    total_km: int,
    expense_type: str,
    cost: float,
    description: Optional[str] = None
) -> Maintenance:
    """
    Inserisce un nuovo record di manutenzione.
    """
    new_maintenance = Maintenance(
        date=date_obj,
        total_km=total_km,
        expense_type=expense_type,
        cost=cost,
        description=description
    )

    db.add(new_maintenance)
    db.commit()
    db.refresh(new_maintenance)
    return new_maintenance