import streamlit as st # <--- Nuovo Import per Cache
from typing import List, Optional
from datetime import date
from sqlalchemy import func, desc, and_, or_
from sqlalchemy.orm import Session
from src.database.models import Refueling, Maintenance, AppSettings, Reminder, ReminderHistory

# ==========================================
# SEZIONE: GESTIONE RIFORNIMENTI (Refueling)
# ==========================================

# NOTE SU CACHE: 
# Usiamo ttl=300 (5 minuti) per le query frequenti.
# Usiamo _db con underscore per evitare che Streamlit provi a hashare la sessione DB.

@st.cache_data(ttl=300, show_spinner=False)
def get_all_refuelings(_db: Session, user_id: str) -> List[Refueling]:
    """Restituisce storico filtrato per utente (Cachato)."""
    return _db.query(Refueling).filter(Refueling.user_id == user_id).order_by(Refueling.date.desc()).all()

@st.cache_data(ttl=300, show_spinner=False)
def get_last_refueling(_db: Session, user_id: str) -> Optional[Refueling]:
    """Recupera l'ultimo inserimento dell'utente (Cachato)."""
    return _db.query(Refueling).filter(Refueling.user_id == user_id).order_by(desc(Refueling.date)).first()

@st.cache_data(ttl=300, show_spinner=False)
def get_max_km(_db: Session, user_id: str) -> int:
    """Max KM dell'utente (Cachato)."""
    max_km = _db.query(func.max(Refueling.total_km)).filter(Refueling.user_id == user_id).scalar()
    return max_km if max_km is not None else 0

def get_neighbors(db: Session, user_id: str, target_date: date) -> dict:
    """Trova record adiacenti solo tra quelli dell'utente. (No Cache - usato in validazione puntuale)"""
    prev_rec = db.query(Refueling).filter(and_(Refueling.user_id == user_id, Refueling.date < target_date)).order_by(desc(Refueling.date)).first()
    next_rec = db.query(Refueling).filter(and_(Refueling.user_id == user_id, Refueling.date > target_date)).order_by(Refueling.date.asc()).first()
    return {"prev": prev_rec, "next": next_rec}

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
    
    # 3. Pulizia Cache (Fondamentale per vedere il nuovo dato)
    st.cache_data.clear()
    
    return new_refueling

def update_refueling(db: Session, user_id: str, record_id: int, new_data: dict):
    """Aggiorna un record solo se appartiene all'utente (Sicurezza)."""
    record = db.query(Refueling).filter(and_(Refueling.id == record_id, Refueling.user_id == user_id)).first()
    if record:
        for key, value in new_data.items():
            setattr(record, key, value)
        db.commit()
        db.refresh(record)
        
        # Pulizia Cache
        st.cache_data.clear()
        
        return record
    return None

def delete_refueling(db: Session, user_id: str, record_id: int) -> bool:
    """Elimina un record solo se appartiene all'utente."""
    record = db.query(Refueling).filter(and_(Refueling.id == record_id, Refueling.user_id == user_id)).first()
    if record:
        db.delete(record)
        db.commit()
        
        # Pulizia Cache
        st.cache_data.clear()
        
        return True
    return False

# ==========================================
# SEZIONE: GESTIONE MANUTENZIONE (Maintenance)
# ==========================================

@st.cache_data(ttl=300, show_spinner=False)
def get_all_maintenances(_db: Session, user_id: str) -> List[Maintenance]:
    """Recupera storico manutenzioni (Cachato)."""
    return _db.query(Maintenance).filter(Maintenance.user_id == user_id).order_by(Maintenance.date.desc()).all()

def create_maintenance(
    db: Session,
    user_id: str,
    date_obj: date,
    total_km: int,
    expense_type: str,
    cost: float,
    description: Optional[str] = None,
    expiry_km: Optional[int] = None,
    expiry_date: Optional[date] = None
) -> Maintenance:
    """Crea e persiste un nuovo record di manutenzione."""
    new_maintenance = Maintenance(
        user_id=user_id,
        date=date_obj,
        total_km=total_km,
        expense_type=expense_type,
        cost=cost,
        description=description,
        expiry_km=expiry_km,
        expiry_date=expiry_date
    )

    db.add(new_maintenance)
    db.commit()
    db.refresh(new_maintenance)
    
    # Pulizia Cache
    st.cache_data.clear()
    
    return new_maintenance

def delete_maintenance(db: Session, user_id: str, record_id: int) -> bool:
    record = db.query(Maintenance).filter(and_(Maintenance.id == record_id, Maintenance.user_id == user_id)).first()
    if record:
        db.delete(record)
        db.commit()
        
        # Pulizia Cache
        st.cache_data.clear()
        return True
    return False

def update_maintenance(db: Session, user_id: str, record_id: int, new_data: dict) -> bool:
    record = db.query(Maintenance).filter(and_(Maintenance.id == record_id, Maintenance.user_id == user_id)).first()
    if record:
        for key, value in new_data.items():
            setattr(record, key, value)
        db.commit()
        db.refresh(record)
        
        # Pulizia Cache
        st.cache_data.clear()
        return True
    return False

def get_future_maintenance_by_type(db: Session, user_id: str, expense_type: str) -> Optional[Maintenance]:
    """
    Cerca se esiste già un record di manutenzione per questo tipo (es. 'Tagliando')
    che ha una scadenza futura impostata (Km o Data).
    """
    return db.query(Maintenance).filter(
        Maintenance.user_id == user_id,
        Maintenance.expense_type == expense_type,
        or_(
            Maintenance.expiry_km != None,
            Maintenance.expiry_date != None
        )
    ).order_by(Maintenance.date.desc()).first()

def get_all_active_deadlines(db: Session, user_id: str) -> List[Maintenance]:
    """
    Recupera TUTTE le manutenzioni che hanno una scadenza impostata (Km o Data).
    Serve per il calcolo del Car Health Score.
    """
    return db.query(Maintenance).filter(
        Maintenance.user_id == user_id,
        or_(
            Maintenance.expiry_km != None,
            Maintenance.expiry_date != None
        )
    ).all()

# ==========================================
# SEZIONE: GESTIONE REMINDERS
# ==========================================

@st.cache_data(ttl=300, show_spinner=False)
def get_active_reminders(_db: Session, user_id: str) -> List[Reminder]:
    """Recupera solo i promemoria attivi dell'utente."""
    return _db.query(Reminder).filter(
        and_(Reminder.user_id == user_id, Reminder.is_active == True)
    ).all()

def create_reminder(
    db: Session, 
    user_id: str, 
    title: str, 
    frequency_km: Optional[int], 
    frequency_days: Optional[int],
    current_km: int,
    current_date: date,
    notes: Optional[str] = None
) -> Reminder:
    """Crea un nuovo promemoria (Km o Giorni o entrambi)."""
    new_reminder = Reminder(
        user_id=user_id,
        title=title,
        frequency_km=frequency_km,
        frequency_days=frequency_days,
        last_km_check=current_km,
        last_date_check=current_date,
        is_active=True,
        notes=notes
    )
    db.add(new_reminder)
    db.commit()
    db.refresh(new_reminder)
    st.cache_data.clear()
    return new_reminder

def log_reminder_execution(
    db: Session, 
    user_id: str, 
    reminder_id: int, 
    check_date: date, 
    check_km: int, 
    notes: str = ""
):
    """
    Azione 'Mark as Done':
    1. Crea record nello storico.
    2. Aggiorna l'ultimo controllo del reminder padre.
    """
    # 1. Crea Log
    history_entry = ReminderHistory(
        reminder_id=reminder_id,
        user_id=user_id,
        date_checked=check_date,
        km_checked=check_km,
        notes=notes
    )
    db.add(history_entry)
    
    # 2. Aggiorna Padre
    rem = db.query(Reminder).filter(and_(Reminder.id == reminder_id, Reminder.user_id == user_id)).first()
    if rem:
        rem.last_km_check = check_km
        rem.last_date_check = check_date
    
    db.commit()
    st.cache_data.clear()
    return True

def update_reminder(
    db: Session, 
    user_id: str, 
    reminder_id: int, 
    title: str, 
    freq_km: Optional[int], 
    freq_days: Optional[int], 
    notes: str
):
    """Aggiorna la definizione di un reminder esistente."""
    rem = db.query(Reminder).filter(and_(Reminder.id == reminder_id, Reminder.user_id == user_id)).first()
    if rem:
        rem.title = title
        rem.frequency_km = freq_km
        rem.frequency_days = freq_days
        rem.notes = notes
        db.commit()
        db.refresh(rem)
        st.cache_data.clear()
        return True
    return False

def delete_reminder(db: Session, user_id: str, reminder_id: int) -> bool:
    rem = db.query(Reminder).filter(and_(Reminder.id == reminder_id, Reminder.user_id == user_id)).first()
    if rem:
        # Nota: Se mettiamo cascade delete nel DB, history si cancella da sola.
        # Altrimenti qui dovremmo cancellare prima la history manualmnete. 
        # Per ora assumiamo un soft delete o gestione DB.
        db.delete(rem)
        db.commit()
        st.cache_data.clear()
        return True
    return False

def get_reminder_history(db: Session, user_id: str, limit: int = 10) -> List[ReminderHistory]:
    """
    Recupera gli ultimi N log di esecuzione routine.
    Eager loading (.join) non strettamente necessario con lazy load, 
    ma SQLAlchemy gestirà la relazione grazie a models.py.
    """
    return db.query(ReminderHistory).filter(
        ReminderHistory.user_id == user_id
    ).order_by(desc(ReminderHistory.date_checked)).limit(limit).all()

# ==========================================
# SEZIONE: SETTINGS
# ==========================================

@st.cache_data(ttl=300, show_spinner=False)
def get_settings(_db: Session, user_id: str) -> AppSettings:
    settings = _db.query(AppSettings).filter(AppSettings.user_id == user_id).first()
    
    # Default Labels se non esistono
    default_labels = ["Controllo Livello Olio", "Pressione Pneumatici", "Liquido Tergicristalli", "Inversione Gomme"]
    
    if not settings:
        settings = AppSettings(
            user_id=user_id,
            reminder_types=default_labels # Set default
        )
        _db.add(settings)
        _db.commit()
        _db.refresh(settings)
    
    # Fallback se il campo nel DB è None (es. vecchi record)
    if settings.reminder_types is None:
        settings.reminder_types = default_labels
        # Non facciamo commit qui per velocità, lo farà il prossimo update
        
    return settings

def update_settings(
    db: Session, 
    user_id: str, 
    fluctuation: float, 
    max_cost: float, 
    alert_threshold: float,
    custom_labels: List[str]
):
    settings = db.query(AppSettings).filter(AppSettings.user_id == user_id).first()
    if not settings:
        settings = AppSettings(user_id=user_id)
        db.add(settings)
    
    settings.price_fluctuation_cents = fluctuation
    settings.max_total_cost = max_cost
    settings.max_accumulated_partial_cost = alert_threshold
    settings.reminder_types = custom_labels # Salva JSON/Array
    
    db.commit()
    db.refresh(settings)
    st.cache_data.clear()
    return settings