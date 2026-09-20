import pandas as pd

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
        
        # Formattazione Scadenze
        scadenza_str = "-"
        if r.expiry_km:
            scadenza_str = f"A {r.expiry_km:,} Km"
        elif r.expiry_date:
            scadenza_str = f"Il {r.expiry_date.strftime('%d/%m/%Y')}"

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