from datetime import date
from src.database import crud

def calculate_car_health_score(db, user_id, current_km):
    """
    Calcola un punteggio da 0 a 100 sulla salute dell'auto.
    Start: 100.
    Malus: Scadenze non rispettate.
    """
    score = 100
    today = date.today()
    overdue_items = []
    
    # 1. Controllo Manutenzioni Scadute (Pesanti)
    # Recuperiamo TUTTE le manutenzioni con scadenze attive (metodo nuovo)
    deadlines = crud.get_all_active_deadlines(db, user_id)
    
    for maint in deadlines:
        # Check Km
        if maint.expiry_km and current_km > maint.expiry_km:
            score -= 20 # Penalità alta per manutenzione meccanica
            overdue_items.append(f"Scaduto: {maint.expense_type} (Km)")
            
        # Check Data
        elif maint.expiry_date and today > maint.expiry_date:
            score -= 15 # Penalità medio-alta
            overdue_items.append(f"Scaduto: {maint.expense_type} (Data)")

    # 2. Controllo Reminder Scaduti (Routine)
    active_reminders = crud.get_active_reminders(db, user_id)
    
    for rem in active_reminders:
        if rem.frequency_km and (current_km - rem.last_km_check) >= rem.frequency_km:
            score -= 10 # Penalità media
            overdue_items.append(f"Routine: {rem.title} (Km)")
            
        elif rem.frequency_days and (today - rem.last_date_check).days >= rem.frequency_days:
            score -= 5 # Penalità lieve
            overdue_items.append(f"Routine: {rem.title} (Tempo)")

    # Cap del punteggio (0 - 100)
    final_score = max(0, min(100, score))
    
    return final_score, overdue_items