import streamlit as st
from datetime import date
from typing import Optional

# ==========================================
# SEZIONE: RIFORNIMENTI (Fuel Forms)
# ==========================================

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
    last_km_known: int = 0, # Nuovo parametro per il Tooltip
    key_suffix: str = "add" # Identificativo univoco del form
) -> dict:
    """
    Renderizza i widget per l'input dati rifornimento (usato sia in Add che Edit).
    Restituisce un dizionario con i valori inseriti.
    """
    # === Riga 1: Data e Prezzo ===
    row1_c1, row1_c2 = st.columns(2)
    
    row1_c1.markdown("**Data**")
    d_date = row1_c1.date_input("Data", value=default_date, label_visibility="collapsed")
    
    # Gestione dello stato del prezzo per permettere l'incremento/decremento tramite bottoni
    slider_key = f"price_slider_{key_suffix}"
    last_default_key = f"last_default_price_{key_suffix}"
    
    if last_default_key not in st.session_state or st.session_state[last_default_key] != default_price:
        safe_default = max(min_price, min(default_price, max_price))
        st.session_state[slider_key] = float(f"{safe_default:.3f}")
        st.session_state[last_default_key] = default_price

    row1_c2.markdown("**Prezzo €/L**<span class='mobile-inline-price'></span>", unsafe_allow_html=True)
    
    col_left, col_slider, col_right = row1_c2.columns([1.5, 7, 1.5], vertical_alignment="center")
    
    btn_left = col_left.form_submit_button("◀", width="stretch")
    btn_right = col_right.form_submit_button("▶", width="stretch")
    
    current_val = st.session_state.get(slider_key, default_price)
    current_val = max(min_price, min(current_val, max_price))
    
    if btn_left:
        current_val = max(min_price, current_val - 0.001)
        st.session_state[slider_key] = float(f"{current_val:.3f}")
    elif btn_right:
        current_val = min(max_price, current_val + 0.001)
        st.session_state[slider_key] = float(f"{current_val:.3f}")
        
    d_price = col_slider.slider(
        "Prezzo €/L", 
        min_value=float(f"{min_price:.3f}"), 
        max_value=float(f"{max_price:.3f}"), 
        step=0.001, 
        format="%.3f",
        key=slider_key,
        label_visibility="collapsed"
    )
    
    # === Riga 2: Odometro e Totale ===
    row2_c1, row2_c2 = st.columns(2)
    
    row2_c1.markdown("**Odometro**")
    d_km = row2_c1.number_input(
        "Odometro", 
        value=default_km,
        step=1, 
        format="%d",
        min_value=0,
        placeholder="Inserisci Km auto...",
        help=f"ℹ️ Ultimo rifornimento registrato a: {last_km_known} Km",
        label_visibility="collapsed"
    )
    
    row2_c2.markdown("**Totale €**")
    d_cost = row2_c2.number_input(
        "Totale €", 
        min_value=0.0, 
        max_value=float(max_cost), 
        value=float(f"{default_cost:.2f}"), 
        step=0.01, format="%.2f",
        label_visibility="collapsed"
    )
    
    d_full = st.checkbox("Pieno Completato?", value=is_full)
    d_notes = st.text_area("Note", value=notes, height=80)
    
    # Nota: Se d_km è None (campo vuoto), ritorniamo 0 o None a seconda di come lo gestisce il validatore.
    # Per sicurezza ritorniamo 0 se è None per evitare crash matematici, ma il validatore dovrà bloccarlo.
    return {
        "date": d_date, "km": d_km if d_km is not None else 0, "price": d_price, 
        "cost": d_cost, "full": d_full, "notes": d_notes
    }