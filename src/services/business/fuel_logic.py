from datetime import date
from services.business.calculations import calculate_stats

def calculate_year_kpis(records, year):
    """Calcola i KPI aggregati per un anno specifico."""
    view_records = [r for r in records if r.date.year == year]
    
    total_liters = sum(r.liters for r in view_records)
    total_cost = sum(r.total_cost for r in view_records)
    avg_price = (total_cost / total_liters) if total_liters > 0 else 0.0
    
    km_est = 0
    if len(view_records) > 1:
        km_vals = [r.total_km for r in view_records]
        km_est = max(km_vals) - min(km_vals)
        
    # Calcolo efficienza min/max
    efficiencies = [
        stats["km_per_liter"] 
        for r in view_records 
        if (stats := calculate_stats(r, records))["km_per_liter"]
    ]
    
    return {
        "total_cost": total_cost,
        "total_liters": total_liters,
        "avg_price": avg_price,
        "km_est": km_est,
        "min_eff": min(efficiencies) if efficiencies else 0.0,
        "max_eff": max(efficiencies) if efficiencies else 0.0,
        "view_records": view_records
    }

def validate_refueling(data, last_km):
    """
    Valida i dati di input.
    Return: (bool, str) -> (is_valid, error_message)
    """
    # Logica originale preservata: se data >= oggi e km < ultimo km noto -> errore
    if data['date'] >= date.today() and data['km'] < last_km:
        return False, f"⛔ Errore Km: impossibile inserire {data['km']} se ultimo era {last_km}."
    
    if data['price'] <= 0 or data['cost'] <= 0:
        return False, "Valori non validi (Prezzo o Costo <= 0)."
        
    return True, ""