from typing import List, Optional
from src.database.models import Refueling

def calculate_stats(current: Refueling, history: List[Refueling]) -> dict:
    """
    Calcola le statistiche per il rifornimento corrente basandosi sullo storico.
    
    Restituisce un dizionario con:
    - delta_km: Km percorsi dall'ultimo rifornimento (qualsiasi).
    - km_per_liter: Efficienza (solo se calcolabile).
    - days_since_last: Giorni passati dall'ultimo rifornimento.
    """
    stats = {
        "delta_km": 0,
        "km_per_liter": None,
        "days_since_last": 0
    }

    # 1. Troviamo il rifornimento immediatamente precedente (per il delta km)
    # Assumiamo che 'history' sia ordinata decrescente (dal più recente al più vecchio)
    # Quindi il primo elemento dopo 'current' è il precedente cronologico.
    
    # Filtriamo current dalla lista se presente per evitare confronti con se stesso
    past_records = [r for r in history if r.date < current.date]
    
    if not past_records:
        return stats  # È il primo record assoluto, niente calcoli possibili

    previous_record = past_records[0]
    stats["delta_km"] = current.total_km - previous_record.total_km
    stats["days_since_last"] = (current.date - previous_record.date).days

    # 2. Calcolo Consumo (Logica Pieno-su-Pieno)
    if current.is_full_tank:
        # Cerchiamo l'ultimo pieno COMPLETO nel passato
        last_full_refuel = None
        liters_consumed = current.liters
        
        found_previous_full = False
        
        for record in past_records:
            if record.is_full_tank:
                last_full_refuel = record
                found_previous_full = True
                break
            else:
                # È un parziale: accumuliamo i litri
                liters_consumed += record.liters
        
        if found_previous_full and last_full_refuel:
            # Abbiamo un intervallo valido tra due pieni
            total_distance = current.total_km - last_full_refuel.total_km
            
            if liters_consumed > 0:
                stats["km_per_liter"] = total_distance / liters_consumed

    return stats