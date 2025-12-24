from typing import List
from database.models import Refueling

# ==========================================
# SEZIONE: LOGICA CALCOLO STATISTICHE (Full-to-Full)
# ==========================================

def calculate_stats(current: Refueling, history: List[Refueling]) -> dict:
    """
    Calcola le metriche (Delta Km, Km/L, Giorni) per il record corrente.
    Utilizza l'algoritmo 'Full-to-Full' per il calcolo preciso del consumo.
    """
    stats = {
        "delta_km": 0,
        "km_per_liter": None,
        "days_since_last": 0
    }

    # 1. Recupero storico precedente
    # Ordiniamo per data decrescente per avere il record più recente all'indice 0
    past_records = sorted(
        [r for r in history if r.date < current.date],
        key=lambda x: x.date,
        reverse=True
    )

    if not past_records:
        return stats

    # 2. Calcolo Delta Base (Km e Tempo rispetto all'ultimo inserimento)
    prev_record = past_records[0]
    stats["delta_km"] = current.total_km - prev_record.total_km
    stats["days_since_last"] = (current.date - prev_record.date).days

    # 3. Calcolo Consumo Reale (Algoritmo Full-to-Full)
    # Si calcola solo se il rifornimento attuale è un Pieno
    if current.is_full_tank:
        liters_consumed = current.liters
        last_full_refuel = None
        found_full = False

        # 3a. Backtracking: Risale lo storico accumulando i litri dei parziali
        for record in past_records:
            if record.is_full_tank:
                last_full_refuel = record
                found_full = True
                break
            liters_consumed += record.liters

        # 3b. Calcolo finale se trovato un pieno di riferimento ("Anchor Point")
        if found_full and last_full_refuel and liters_consumed > 0:
            distance = current.total_km - last_full_refuel.total_km
            stats["km_per_liter"] = distance / liters_consumed

    return stats


# ==========================================
# SEZIONE: LOGICA ALERT (Parziali)
# ==========================================

def check_partial_accumulation(history: List[Refueling]) -> dict:
    """
    Verifica se ci sono troppi rifornimenti parziali consecutivi accumulati.
    Restituisce il costo totale accumulato dall'ultimo pieno.
    """
    accumulated_cost = 0.0
    count = 0
    
    # Ordine decrescente: dal più recente al più vecchio
    sorted_history = sorted(history, key=lambda x: x.date, reverse=True)
    
    for r in sorted_history:
        if r.is_full_tank:
            # Trovato un pieno (reset del contatore), stop analisi
            break
        else:
            # È un parziale, accumuliamo costo e conteggio
            accumulated_cost += r.total_cost
            count += 1
            
    return {
        "accumulated_cost": accumulated_cost,
        "partials_count": count
    }