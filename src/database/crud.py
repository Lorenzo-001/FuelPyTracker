from typing import List, Optional
from datetime import date
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from database.models import Refueling, Maintenance

# ==========================================
# SEZIONE: GESTIONE RIFORNIMENTI (Refueling)
# ==========================================

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
    """Crea e persiste un nuovo record di rifornimento."""
    new_refueling = Refueling(
        date=date_obj,
        total_km=total_km,
        price_per_liter=price_per_liter,
        total_cost=total_cost,
        liters=liters,
        is_full_tank=is_full_tank,
        notes=notes
    )
    
    # 1. Add & Commit transazione
    db.add(new_refueling)
    db.commit()
    
    # 2. Refresh per ottenere ID generato
    db.refresh(new_refueling)
    return new_refueling

def get_all_refuelings(db: Session) -> List[Refueling]:
    """Restituisce storico completo ordinato per data (DESC)."""
    return db.query(Refueling).order_by(Refueling.date.desc()).all()

def get_last_refueling(db: Session) -> Optional[Refueling]:
    """Recupera l'ultimo inserimento cronologico (utile per Undo)."""
    return db.query(Refueling).order_by(desc(Refueling.date)).first()

def get_max_km(db: Session) -> int:
    """Restituisce valore odometro massimo registrato (per validazione input)."""
    max_km = db.query(func.max(Refueling.total_km)).scalar()
    return max_km if max_km is not None else 0

def get_neighbors(db: Session, target_date: date) -> dict:
    """
    Trova record adiacenti (Prev/Next) rispetto a una data target.
    Essenziale per 'Sandwich Validation' in fase di modifica.
    """
    prev_rec = db.query(Refueling).filter(Refueling.date < target_date).order_by(desc(Refueling.date)).first()
    next_rec = db.query(Refueling).filter(Refueling.date > target_date).order_by(Refueling.date.asc()).first()
    return {"prev": prev_rec, "next": next_rec}

def update_refueling(db: Session, record_id: int, new_data: dict):
    """Aggiorna puntualmente i campi specificati in new_data."""
    record = db.query(Refueling).filter(Refueling.id == record_id).first()
    if record:
        for key, value in new_data.items():
            setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record
    return None

def delete_refueling(db: Session, record_id: int) -> bool:
    """Elimina fisicamente un record dato l'ID."""
    record = db.query(Refueling).filter(Refueling.id == record_id).first()
    if record:
        db.delete(record)
        db.commit()
        return True
    return False

# ==========================================
# SEZIONE: GESTIONE MANUTENZIONE (Maintenance)
# ==========================================

def create_maintenance(
    db: Session,
    date_obj: date,
    total_km: int,
    expense_type: str,
    cost: float,
    description: Optional[str] = None
) -> Maintenance:
    """Crea e persiste un nuovo record di manutenzione."""
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