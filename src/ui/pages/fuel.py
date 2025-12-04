import streamlit as st
from datetime import date
from database.core import get_db
from database import crud
from ui.components import grids

def render():
    st.header("⛽ Gestione Rifornimenti")

    db = next(get_db())
    
    # 1. Recupero Dati Contesto
    last_record = crud.get_last_refueling(db)
    settings = crud.get_settings(db)
    
    last_km = last_record.total_km if last_record else 0
    last_price = last_record.price_per_liter if last_record else 1.650 # Fallback se DB vuoto

    # 2. Calcolo Range Dinamici
    range_val = settings.price_fluctuation_cents
    min_price_allow = max(0.0, last_price - range_val)
    max_price_allow = last_price + range_val
    
    # --- FORM ---
    with st.expander("Aggiungi Nuovo Rifornimento", expanded=True):
        # Mostriamo il range attivo E il massimale di spesa come informazione visiva
        st.caption(
            f"💡 Range prezzi: **{min_price_allow:.3f}** - **{max_price_allow:.3f}** €/L  •  "
            f"💰 Max Spesa: **{settings.max_total_cost:.2f}** € (Configurabili in Impostazioni)"
        )
        
        with st.form("fuel_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            d_date = c1.date_input("Data", value=date.today())
            
            d_km = c1.number_input("Odometro (Km)", value=last_km, step=1, format="%d")
            
            # SLIDER per il Prezzo al Litro
            d_price = c2.slider(
                "Prezzo al Litro (€)", 
                min_value=float(f"{min_price_allow:.3f}"), 
                max_value=float(f"{max_price_allow:.3f}"), 
                value=float(f"{last_price:.3f}"), 
                step=0.001, 
                format="%.3f",
                help="Muovi il cursore per selezionare il prezzo esatto."
            )

            # Input Costo con Max Settings
            d_cost = c2.number_input(
                "Spesa Totale (€)", 
                min_value=0.0, 
                max_value=settings.max_total_cost, # Vincolo da Settings
                step=0.01, 
                format="%.2f"
            )
            
            d_full = st.checkbox("Pieno Completato?", value=True)
            d_notes = st.text_area("Note")
            
            if st.form_submit_button("Salva"):
                _handle_submit(db, d_date, d_km, last_km, d_price, d_cost, d_full, d_notes)

    # --- STORICO CON DELETE ---
    st.divider()
    st.subheader("Storico Rifornimenti")
    
    # Recuperiamo gli ultimi 20 record per non intasare la pagina
    all_records = crud.get_all_refuelings(db) 
    
    if all_records:
        # Mostriamo la tabella classica per una visione d'insieme
        df_display = grids.build_fuel_dataframe(all_records)
        st.dataframe(df_display.drop(columns=["_obj"]), width="stretch", hide_index=True)
        
        st.write("")
        st.subheader("Gestione Rapida (Ultimi 5)")
        
        # Loop sugli ultimi 5 record per permettere cancellazione rapida
        for r in all_records[:5]:
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 3, 1])
                c1.text(r.date.strftime("%d/%m/%Y"))
                c2.text(f"{r.total_km} km")
                c3.text(f"€ {r.total_cost:.2f}")
                c4.caption(r.notes if r.notes else "-")
                
                # Pulsante Delete univoco per riga
                if c5.button("🗑️", key=f"del_{r.id}", help="Elimina record"):
                    crud.delete_refueling(db, r.id)
                    st.success("Record eliminato!")
                    st.cache_data.clear()
                    st.rerun()
                st.divider()
    else:
        st.info("Nessun dato.")

    db.close()

def _handle_submit(db, d_date, d_km, last_km, d_price, d_cost, d_full, d_notes):
    if d_date >= date.today() and d_km < last_km:
        st.error(f"⛔ Errore Km: non puoi inserire {d_km} km se l'ultimo era {last_km}.")
        return
    
    if d_price <= 0 or d_cost <= 0:
        st.error("Valori non validi.")
        return

    try:
        liters = d_cost / d_price
        crud.create_refueling(db, d_date, d_km, d_price, d_cost, liters, d_full, d_notes)
        st.success(f"✅ Rifornimento salvato! ({liters:.2f} L)")
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Errore DB: {e}")