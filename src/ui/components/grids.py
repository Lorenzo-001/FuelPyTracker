import pandas as pd
from services.calculations import calculate_stats

def build_fuel_dataframe(records: list) -> pd.DataFrame:
    """
    1. Trasforma i record ORM in un DataFrame Pandas per la UI.
    2. Arricchisce i dati con calcoli (Delta Km, Km/L).
    """
    data_list = []
    
    for r in records:
        # Calcolo metriche puntuali
        stats = calculate_stats(r, records)
        
        # Formattazione condizionale
        kml_str = f"{stats['km_per_liter']:.2f}" if stats['km_per_liter'] else "-"
        delta_str = f"+{stats['delta_km']}" if stats['delta_km'] > 0 else "-"
        
        data_list.append({
            "ID": r.id,
            "Data": r.date,
            "Km Totali": r.total_km,
            "Delta Km": delta_str,
            "Prezzo (€/L)": f"{r.price_per_liter:.3f}",
            "Spesa (€)": f"{r.total_cost:.2f}",
            "Litri": f"{r.liters:.2f}",
            "Km/L": kml_str,
            "Pieno": "✅" if r.is_full_tank else "❌",
            "_obj": r  # Riferimento interno nascosto
        })
        
    return pd.DataFrame(data_list)

def build_maintenance_dataframe(records: list) -> pd.DataFrame:
    """
    Formatta lo storico manutenzioni aggiungendo icone visive per categoria.
    """
    # Mappa icone per categoria
    icons = {
        "Tagliando": "🛠️",
        "Gomme": "🛞",
        "Batteria": "🔋",
        "Revisione": "⚖️",
        "Bollo": "📄",
        "Riparazione": "🔧",
        "Altro": "⚙️"
    }

    data_list = []
    for r in records:
        icon = icons.get(r.expense_type, "⚙️")
        
        data_list.append({
            "ID": r.id,
            "Data": r.date,
            "Tipo": f"{icon} {r.expense_type}", # Aggiunge icona al testo
            "Km": r.total_km,
            "Costo (€)": f"{r.cost:.2f}",
            "Descrizione": r.description if r.description else "-",
            "_obj": r
        })
        
    return pd.DataFrame(data_list)