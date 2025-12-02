import streamlit as st
from datetime import date
from database.core import get_db
from database import crud

def render():
    """Vista gestione Manutenzioni (Tagliandi, Gomme, etc)."""
    st.header("🔧 Registro Manutenzioni")

    # 1. Form Inserimento
    with st.form("maintenance_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        m_date = c1.date_input("Data", value=date.today())
        m_km = c1.number_input("Km al momento", min_value=0, step=1)
        
        m_type = c2.selectbox("Tipo", ["Tagliando", "Gomme", "Batteria", "Revisione", "Altro"])
        m_cost = c2.number_input("Costo (€)", min_value=0.0, step=1.0)
        m_desc = st.text_area("Descrizione")

        if st.form_submit_button("Salva"):
            _handle_submit(m_date, m_km, m_type, m_cost, m_desc)

def _handle_submit(d_date, d_km, d_type, d_cost, d_desc):
    """Logica di salvataggio manutenzione."""
    if d_cost <= 0:
        st.warning("⚠️ Il costo deve essere maggiore di zero.")
        return

    db = next(get_db())
    try:
        crud.create_maintenance(db, d_date, d_km, d_type, d_cost, d_desc)
        st.success("✅ Intervento registrato.")
    except Exception as e:
        st.error(f"Errore DB: {e}")
    finally:
        db.close()