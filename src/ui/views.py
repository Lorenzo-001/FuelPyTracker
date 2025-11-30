import streamlit as st
from datetime import date
from src.database.core import get_db
from src.database import crud

def render_dashboard():
    """
    Renderizza la pagina principale con i riepiloghi.
    """
    st.header("Dashboard Riepilogativa")
    st.info("🚧 I grafici verranno implementati nel prossimo step!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Ultimo Prezzo", value="--- €/L")
    with col2:
        st.metric(label="Media Consumi", value="--- km/L")

def render_fuel_page():
    """
    Form per inserimento Rifornimenti.
    """
    st.header("⛽ Gestione Rifornimenti")

    # --- FORM DI INSERIMENTO ---
    with st.expander("Aggiungi Nuovo Rifornimento", expanded=True):
        with st.form("fuel_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                d_date = st.date_input("Data", value=date.today())
                d_km = st.number_input("Chilometri Totali (Odometer)", min_value=0, step=1, format="%d")
            
            with col2:
                d_price = st.number_input("Prezzo al Litro (€)", min_value=0.0, step=0.001, format="%.3f")
                d_cost = st.number_input("Spesa Totale (€)", min_value=0.0, step=0.01, format="%.2f")

            d_full = st.checkbox("Pieno Completato?", value=True)
            d_notes = st.text_area("Note (Opzionale)")

            submitted = st.form_submit_button("Salva Rifornimento")

            if submitted:
                if d_price > 0 and d_cost > 0:
                    # Calcolo automatico litri
                    calculated_liters = d_cost / d_price
                    
                    # Gestione Sessione DB
                    db = next(get_db())
                    try:
                        crud.create_refueling(
                            db=db,
                            date_obj=d_date,
                            total_km=d_km,
                            price_per_liter=d_price,
                            total_cost=d_cost,
                            liters=calculated_liters,
                            is_full_tank=d_full,
                            notes=d_notes
                        )
                        st.success(f"✅ Rifornimento salvato! (Litri calcolati: {calculated_liters:.2f})")
                    except Exception as e:
                        st.error(f"Errore durante il salvataggio: {e}")
                    finally:
                        db.close()
                else:
                    st.warning("⚠️ Inserisci un prezzo e un costo validi.")

    # --- TABELLA STORICO (Anteprima) ---
    st.divider()
    st.subheader("Storico Recente")
    
    # Recuperiamo i dati per mostrare che funziona
    db = next(get_db())
    records = crud.get_all_refuelings(db)
    db.close()

    if records:
        # Creiamo una lista di dizionari per farla digerire a Streamlit
        data = [
            {
                "Data": r.date,
                "Km": r.total_km,
                "Prezzo": f"€ {r.price_per_liter:.3f}",
                "Spesa": f"€ {r.total_cost:.2f}",
                "Litri": f"{r.liters:.2f}",
                "Pieno": "Sì" if r.is_full_tank else "No"
            }
            for r in records
        ]
        st.dataframe(data, width="stretch", hide_index=True)
    else:
        st.info("Nessun rifornimento registrato.")


def render_maintenance_page():
    """
    Form per inserimento Manutenzioni.
    """
    st.header("🔧 Registro Manutenzioni")

    with st.form("maintenance_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            m_date = st.date_input("Data Intervento", value=date.today())
            m_km = st.number_input("Chilometri al momento", min_value=0, step=1, format="%d")
        
        with col2:
            m_type = st.selectbox("Tipo Intervento", ["Tagliando", "Gomme", "Batteria", "Revisione", "Bollo", "Altro"])
            m_cost = st.number_input("Costo (€)", min_value=0.0, step=1.0, format="%.2f")

        m_desc = st.text_area("Dettagli Intervento")
        
        submitted = st.form_submit_button("Salva Manutenzione")

        if submitted:
            db = next(get_db())
            try:
                crud.create_maintenance(
                    db=db,
                    date_obj=m_date,
                    total_km=m_km,
                    expense_type=m_type,
                    cost=m_cost,
                    description=m_desc
                )
                st.success("✅ Intervento registrato correttamente!")
            except Exception as e:
                st.error(f"Errore: {e}")
            finally:
                db.close()