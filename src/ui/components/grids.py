import pandas as pd
from services.business.calculations import calculate_stats

# ==========================================
# SEZIONE: RIFORNIMENTI (Fuel Grid)
# ==========================================

def build_fuel_dataframe(records: list) -> pd.DataFrame:
    """
    Costruisce il DataFrame per la visualizzazione dello storico rifornimenti.
    
    Logica applicata:
    1. Calcolo metriche puntuali (Delta Km, Km/L) tramite service dedicato.
    2. Formattazione visuale (es. aggiunta simboli, decimali).
    3. Mantenimento oggetto originale (_obj) per operazioni CRUD.
    """
    data_list = []
    
    for r in records:
        # Calcolo metriche avanzate (es. Full-to-Full)
        stats = calculate_stats(r, records)
        
        # Formattazione Dati
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
            "_obj": r  # Hidden object per logica interna
        })
        
    return pd.DataFrame(data_list)


# ==========================================
# SEZIONE: MANUTENZIONE (Maintenance Grid)
# ==========================================

def build_maintenance_dataframe(records: list) -> pd.DataFrame:
    """
    Costruisce il DataFrame per lo storico manutenzioni.
    Include la logica di mappatura icone per categoria.
    """
    # Mappa Icone Categoria
    ICONS_MAP = {
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
        icon = ICONS_MAP.get(r.expense_type, "⚙️")
        
        data_list.append({
            "ID": r.id,
            "Data": r.date,
            "Tipo": f"{icon} {r.expense_type}", 
            "Km": r.total_km,
            "Costo (€)": f"{r.cost:.2f}",
            "Descrizione": r.description if r.description else "-",
            "_obj": r
        })
        
    return pd.DataFrame(data_list)