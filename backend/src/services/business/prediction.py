from datetime import date, timedelta

def calculate_daily_usage_rate(refuelings) -> float:
    """
    Calcola la media di Km percorsi al giorno basandosi sugli ultimi rifornimenti.
    Ritorna: km/giorno (float).
    """
    if not refuelings or len(refuelings) < 2:
        return 0.0

    # Ordiniamo per data
    sorted_refs = sorted(refuelings, key=lambda x: x.date)
    
    # Prendiamo solo gli ultimi 6 mesi (o tutti se meno recenti) per realismo
    first_ref = sorted_refs[0]
    last_ref = sorted_refs[-1]
    
    delta_km = last_ref.total_km - first_ref.total_km
    delta_days = (last_ref.date - first_ref.date).days
    
    if delta_days <= 0 or delta_km <= 0:
        return 0.0
        
    return delta_km / delta_days

def predict_reach_date(current_km: int, target_km: int, daily_rate: float) -> date | None:
    """
    Stimiamo la data in cui si raggiungerà il target_km.
    """
    if daily_rate <= 0 or target_km <= current_km:
        return None
        
    km_remaining = target_km - current_km
    days_to_go = int(km_remaining / daily_rate)
    
    return date.today() + timedelta(days=days_to_go)