import streamlit as st

def render_dashboard():
    """
    Renderizza la pagina principale con i riepiloghi.
    """
    st.header("Dashboard Riepilogativa")
    st.info("Qui verranno visualizzati i grafici di andamento prezzi e consumi.")
    
    # Placeholder per il layout futuro
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Ultimo Prezzo")
        st.text("--- €/L")
    with col2:
        st.markdown("### Media Consumi")
        st.text("--- km/L")

def render_fuel_page():
    """
    Renderizza la pagina per la gestione dei Rifornimenti.
    """
    st.header("Gestione Rifornimenti")
    st.text("Utilizza questa sezione per inserire nuovi rifornimenti o visualizzare lo storico.")
    
    # Placeholder per la tabella dati
    st.subheader("Storico Rifornimenti")
    st.text("Tabella dati in caricamento...")

def render_maintenance_page():
    """
    Renderizza la pagina per la gestione delle Manutenzioni.
    """
    st.header("Registro Manutenzioni")
    st.text("Qui potrai tracciare tagliandi, cambi gomme e altre spese.")