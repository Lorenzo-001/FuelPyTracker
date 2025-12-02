from typing import List
from database.models import Refueling

def calculate_stats(current: Refueling, history: List[Refueling]) -> dict:
    """
    Calcola metriche (Delta Km, Km/L, Giorni) per il record corrente basandosi sullo storico.
    """
    stats = {
        "delta_km": 0,
        "km_per_liter": None,
        "days_since_last": 0
    }

    # 1. Filtra record precedenti (escludendo se stesso e futuri)
    # Assumiamo history ordinata decrescente.
    past_records = [r for r in history if r.date < current.date]
    if not past_records:
        return stats

    # 2. Calcolo Delta Km e Tempo (rispetto al record immediatamente precedente)
    prev_record = past_records[0]
    stats["delta_km"] = current.total_km - prev_record.total_km
    stats["days_since_last"] = (current.date - prev_record.date).days

    # 3. Calcolo Consumo Reale (Logica Full-to-Full)
    # Calcolabile solo se il pieno corrente è completo.
    if current.is_full_tank:
        liters_consumed = current.liters
        last_full_refuel = None
        found_full = False

        # 3a. Risale lo storico accumulando litri dei parziali
        for record in past_records:
            if record.is_full_tank:
                last_full_refuel = record
                found_full = True
                break
            liters_consumed += record.liters

        # 3b. Calcola media se trovato un pieno precedente di riferimento
        if found_full and last_full_refuel and liters_consumed > 0:
            distance = current.total_km - last_full_refuel.total_km
            stats["km_per_liter"] = distance / liters_consumed

    return stats