from typing import List, Optional
from datetime import date
from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session
from src.database.models import Refueling, Maintenance, AppSettings

# ==========================================
# SEZIONE: GESTIONE RIFORNIMENTI (Refueling)
# ==========================================

def create_refueling(
    db: Session, 
    user_id: str,
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
        user_id=user_id,
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

def get_all_refuelings(db: Session, user_id: str) -> List[Refueling]:
    """Restituisce storico filtrato per utente."""
    return db.query(Refueling).filter(Refueling.user_id == user_id).order_by(Refueling.date.desc()).all()

def get_last_refueling(db: Session, user_id: str) -> Optional[Refueling]:
    """Recupera l'ultimo inserimento dell'utente."""
    return db.query(Refueling).filter(Refueling.user_id == user_id).order_by(desc(Refueling.date)).first()

def get_max_km(db: Session, user_id: str) -> int:
    """Max KM dell'utente."""
    max_km = db.query(func.max(Refueling.total_km)).filter(Refueling.user_id == user_id).scalar()
    return max_km if max_km is not None else 0

def get_neighbors(db: Session, user_id: str, target_date: date) -> dict:
    """Trova record adiacenti solo tra quelli dell'utente."""
    # Nota: Aggiungiamo il filtro user_id a entrambe le query
    prev_rec = db.query(Refueling).filter(and_(Refueling.user_id == user_id, Refueling.date < target_date)).order_by(desc(Refueling.date)).first()
    next_rec = db.query(Refueling).filter(and_(Refueling.user_id == user_id, Refueling.date > target_date)).order_by(Refueling.date.asc()).first()
    return {"prev": prev_rec, "next": next_rec}

def update_refueling(db: Session, user_id: str, record_id: int, new_data: dict):
    """Aggiorna un record solo se appartiene all'utente (Sicurezza)."""
    record = db.query(Refueling).filter(and_(Refueling.id == record_id, Refueling.user_id == user_id)).first()
    if record:
        for key, value in new_data.items():
            setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return record
    return None

def delete_refueling(db: Session, user_id: str, record_id: int) -> bool:
    """Elimina un record solo se appartiene all'utente."""
    record = db.query(Refueling).filter(and_(Refueling.id == record_id, Refueling.user_id == user_id)).first()
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
    user_id: str,
    date_obj: date,
    total_km: int,
    expense_type: str,
    cost: float,
    description: Optional[str] = None
) -> Maintenance:
    """Crea e persiste un nuovo record di manutenzione."""
    new_maintenance = Maintenance(
        user_id=user_id,
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

def get_all_maintenances(db: Session, user_id: str) -> List[Maintenance]:
    return db.query(Maintenance).filter(Maintenance.user_id == user_id).order_by(Maintenance.date.desc()).all()

def delete_maintenance(db: Session, user_id: str, record_id: int) -> bool:
    record = db.query(Maintenance).filter(and_(Maintenance.id == record_id, Maintenance.user_id == user_id)).first()
    if record:
        db.delete(record)
        db.commit()
        return True
    return False

def update_maintenance(db: Session, user_id: str, record_id: int, new_data: dict) -> bool:
    record = db.query(Maintenance).filter(and_(Maintenance.id == record_id, Maintenance.user_id == user_id)).first()
    if record:
        for key, value in new_data.items():
            setattr(record, key, value)
        db.commit()
        db.refresh(record)
        return True
    return False

# ==========================================
# SEZIONE: SETTINGS
# ==========================================

def get_settings(db: Session, user_id: str) -> AppSettings:
    """Recupera le impostazioni dell'utente. Se non esistono, crea riga per user_id."""
    settings = db.query(AppSettings).filter(AppSettings.user_id == user_id).first()
    if not settings:
        settings = AppSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

def update_settings(db: Session, user_id: str, fluctuation: float, max_cost: float, alert_threshold: float):
    """Aggiorna configurazioni dell'utente specifico."""
    settings = get_settings(db, user_id)
    settings.price_fluctuation_cents = fluctuation
    settings.max_total_cost = max_cost
    settings.max_accumulated_partial_cost = alert_threshold
    db.commit()
    db.refresh(settings)
    return settings