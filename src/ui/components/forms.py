import streamlit as st
from datetime import date
from typing import Optional

def render_refueling_inputs(
    default_date: date, 
    default_km: Optional[int], # Ora accetta None
    default_price: float, 
    default_cost: float, 
    is_full: bool, 
    notes: str, 
    min_price: float, 
    max_price: float, 
    max_cost: float,
    last_km_known: int = 0 # Nuovo parametro per il Tooltip
) -> dict:
    """
    Renderizza i widget per l'input dati rifornimento (usato sia in Add che Edit).
    Restituisce un dizionario con i valori inseriti.
    """
    c1, c2 = st.columns(2)
    
    d_date = c1.date_input("Data", value=default_date)
    
    # Odometro vuoto per default + Tooltip informativo
    d_km = c1.number_input(
        "Odometro", 
        value=default_km,
        step=1, 
        format="%d",
        min_value=0,
        placeholder="Inserisci Km auto...",
        help=f"ℹ️ Ultimo rifornimento registrato a: {last_km_known} Km"
    )
    
    # Slider e input numerici con limiti dinamici
    d_price = c2.slider(
        "Prezzo €/L", 
        min_value=float(f"{min_price:.3f}"), 
        max_value=float(f"{max_price:.3f}"), 
        value=float(f"{default_price:.3f}"), 
        step=0.001, format="%.3f"
    )
    
    d_cost = c2.number_input(
        "Totale €", 
        min_value=0.0, 
        max_value=float(max_cost), 
        value=float(f"{default_cost:.2f}"), 
        step=0.01, format="%.2f"
    )
    
    d_full = st.checkbox("Pieno Completato?", value=is_full)
    d_notes = st.text_area("Note", value=notes, height=80)
    
    # Nota: Se d_km è None (campo vuoto), ritorniamo 0 o None a seconda di come lo gestisce il validatore.
    # Per sicurezza ritorniamo 0 se è None per evitare crash matematici, ma il validatore dovrà bloccarlo.
    return {
        "date": d_date, "km": d_km if d_km is not None else 0, "price": d_price, 
        "cost": d_cost, "full": d_full, "notes": d_notes
    }


def render_maintenance_inputs(
    default_date: date, 
    default_km: int, 
    default_type: str, 
    default_cost: float, 
    default_desc: str
) -> dict:
    """
    Renderizza i widget per l'input dati manutenzione (Add/Edit).
    """
    c1, c2 = st.columns(2)
    
    date_val = c1.date_input("Data", value=default_date)
    km_val = c1.number_input("Odometro", value=default_km, step=1, format="%d")
    
    cat_opts = ["Tagliando", "Gomme", "Batteria", "Revisione", "Bollo", "Riparazione", "Altro"]
    
    # Gestione sicura dell'indice per la selectbox
    try:
        idx_type = cat_opts.index(default_type)
    except ValueError:
        idx_type = 6 # Default su 'Altro' se non trovato
        
    type_val = c2.selectbox("Categoria", cat_opts, index=idx_type)
    
    cost_val = c2.number_input(
        "Costo €", 
        value=float(default_cost), 
        min_value=0.0, 
        step=1.0, 
        format="%.2f"
    )
    
    desc_val = st.text_area("Note / Dettagli", value=default_desc, height=80)
    
    return {
        "date": date_val, "km": km_val, "type": type_val, 
        "cost": cost_val, "desc": desc_val
    }