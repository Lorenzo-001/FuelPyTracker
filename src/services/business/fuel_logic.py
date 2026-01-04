from datetime import date
from src.services.business.calculations import calculate_stats

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

def validate_refueling(new_data, all_records):
    """
    Valida i dati assicurando la coerenza cronologica dei chilometri.
    Controlla che i Km inseriti siano coerenti con i record immediatamente precedenti e successivi.
    
    Args:
        new_data (dict): I dati del form.
        all_records (list): La lista completa di tutti i rifornimenti esistenti.
        
    Return: (bool, str) -> (is_valid, error_message)
    """
    input_km = new_data['km']
    input_date = new_data['date']

    # 1. Controlli Base
    if new_data['price'] <= 0 or new_data['cost'] <= 0:
        return False, "Prezzo e Costo devono essere maggiori di zero."
    
    if input_km <= 0:
        return False, "I chilometri devono essere maggiori di zero."

    # Se non ci sono altri record, va bene tutto (purché > 0)
    if not all_records:
        return True, ""

    # 2. Ordiniamo i record per data per trovare i "vicini"
    sorted_records = sorted(all_records, key=lambda r: r.date)

    prev_record = None
    next_record = None

    # Troviamo il record immediatamente prima e quello immediatamente dopo
    for record in sorted_records:
        if record.date <= input_date:
            prev_record = record # Continuiamo ad aggiornare finché siamo nel passato/presente
        else:
            next_record = record
            break # Appena troviamo una data futura, quello è il "next" e ci fermiamo

    # 3. Controllo Coerenza col Passato (Prev <= Input)
    if prev_record:
        # Se la data è uguale, permettiamo inserimento solo se i km sono >= (es. due rifornimenti stesso giorno)
        if input_km < prev_record.total_km:
            return False, (
                f"⛔ Errore Cronologico: Hai inserito {input_km} Km in data {input_date.strftime('%d/%m/%Y')}, "
                f"ma esiste già un record precedente ({prev_record.date.strftime('%d/%m/%Y')}) "
                f"con {prev_record.total_km} Km. Impossibile scendere di chilometri."
            )

    # 4. Controllo Coerenza col Futuro (Input <= Next)
    if next_record:
        if input_km > next_record.total_km:
            return False, (
                f"⛔ Errore Storico: Hai inserito {input_km} Km nel {input_date.strftime('%Y')}, "
                f"ma esiste un record successivo ({next_record.date.strftime('%d/%m/%Y')}) "
                f"che riporta solo {next_record.total_km} Km. Non puoi avere più km nel passato che nel futuro."
            )

    return True, ""