import streamlit as st
from datetime import date
from database.core import get_db
from database import crud
from ui.components import grids  # Importiamo il componente riutilizzabile

def render():
    """Renderizza la pagina Rifornimenti (Form + Tabella)."""
    st.header("⛽ Gestione Rifornimenti")

    # 1. Setup Contesto (DB & Ultimo Km)
    db = next(get_db())
    last_known_km = crud.get_max_km(db)
    
    # 2. Sezione Form
    with st.expander("Aggiungi Nuovo Rifornimento", expanded=True):
        with st.form("fuel_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            d_date = c1.date_input("Data", value=date.today())
            
            # Default intelligente
            default_km = last_known_km if last_known_km > 0 else 0
            d_km = c1.number_input("Odometro (Km)", value=default_km, step=1, format="%d")
            
            d_price = c2.number_input("Prezzo (€/L)", min_value=0.0, step=0.001, format="%.3f")
            d_cost = c2.number_input("Totale (€)", min_value=0.0, step=0.01, format="%.2f")
            
            d_full = st.checkbox("Pieno Completato?", value=True)
            d_notes = st.text_area("Note")
            
            if st.form_submit_button("Salva"):
                # 3. Validazione & Salvataggio
                _handle_submit(db, d_date, d_km, last_known_km, d_price, d_cost, d_full, d_notes)

    # 4. Sezione Storico (Componente)
    st.divider()
    st.subheader("Storico Rifornimenti")
    records = crud.get_all_refuelings(db)
    db.close()

    if records:
        # Utilizzo del componente 'grid' creato prima
        df_display = grids.build_fuel_dataframe(records)
        st.dataframe(
            df_display.drop(columns=["_obj"]), 
            width="stretch", 
            hide_index=True
        )
    else:
        st.info("Nessun dato in storico.")

def _handle_submit(db, d_date, d_km, last_km, d_price, d_cost, d_full, d_notes):
    """Logica privata di validazione e salvataggio form."""
    if d_date >= date.today() and d_km < last_km:
        st.error(f"⛔ Errore: Km inferiori allo storico ({last_km}).")
        return

    if d_price <= 0 or d_cost <= 0:
        st.warning("⚠️ Prezzi devono essere > 0.")
        return

    try:
        liters = d_cost / d_price
        crud.create_refueling(db, d_date, d_km, d_price, d_cost, liters, d_full, d_notes)
        st.success(f"✅ Salvato! ({liters:.2f} L)")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Errore DB: {e}")