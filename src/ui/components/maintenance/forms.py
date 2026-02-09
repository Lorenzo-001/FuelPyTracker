import streamlit as st
from datetime import date
from typing import Optional

def render_maintenance_inputs(
    default_date: date, 
    default_km: int, 
    default_type: str, 
    default_cost: float, 
    default_desc: str,
    default_expiry_km: Optional[int] = None,
    default_expiry_date: Optional[date] = None
) -> dict:
    """
    Renderizza i widget per l'input dati manutenzione (Add/Edit).
    Aggiornato per gestire le scadenze (Km o Data).
    """
    c1, c2 = st.columns(2)
    
    # Riga 1: Dati Base
    date_val = c1.date_input("Data Intervento", value=default_date)
    km_val = c1.number_input("Odometro al momento", value=default_km, step=1, format="%d")
    
    cat_opts = ["Tagliando", "Gomme", "Batteria", "Revisione", "Bollo", "Riparazione", "Altro"]
    try:
        idx_type = cat_opts.index(default_type)
    except ValueError:
        idx_type = 6 
        
    type_val = c2.selectbox("Categoria", cat_opts, index=idx_type)
    cost_val = c2.number_input("Costo €", value=float(default_cost), min_value=0.0, step=1.0, format="%.2f")
    
    # Riga 2: Descrizione
    desc_val = st.text_area("Note / Dettagli", value=default_desc, height=80)
    
    # Riga 3: Pianificazione Scadenze (Nuova Sezione)
    st.markdown("###### Pianificazione Prossima Scadenza (Opzionale)")
    st.caption("Compila uno dei due campi se vuoi che l'app ti avvisi in futuro.")
    
    ce1, ce2 = st.columns(2)
    
    # Scadenza KM (es. per Tagliandi/Gomme)
    help_km = (
        "Indica a che chilometraggio totale prevedi il prossimo intervento (es. Km attuali + 15.000). "
        "Il sistema calcolerà la data stimata in base al tuo stile di guida."
    )
    exp_km_val = ce1.number_input(
        "Prossima Scadenza (Km)", 
        value=default_expiry_km, 
        min_value=0, 
        step=1000, 
        format="%d",
        help=help_km,
        placeholder="Es. 150000"
    )
    # Convertiamo 0 in None per il DB
    if exp_km_val == 0: exp_km_val = None

    # Scadenza Data (es. per Bollo/Revisione)
    help_date = (
        "Indica la data esatta della scadenza (es. per Bollo o Revisione). "
        "Il sistema attiverà un conto alla rovescia."
    )
    exp_date_val = ce2.date_input(
        "Prossima Scadenza (Data)", 
        value=default_expiry_date, 
        format="DD/MM/YYYY",
        help=help_date, # <--- FIX TOOLTIP
        key="exp_date_picker"
    )
    if exp_date_val == date_val: 
        exp_date_val = None

    return {
        "date": date_val, "km": km_val, "type": type_val, 
        "cost": cost_val, "desc": desc_val,
        "expiry_km": exp_km_val, "expiry_date": exp_date_val
    }