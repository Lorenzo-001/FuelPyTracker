import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from src.database.core import init_db
from src.ui import views

@st.cache_resource
def initialize_app():
    """
    Funzione wrappata con cache_resource.
    Streamlit la eseguirà SOLO una volta all'avvio del server,
    ignorandola ai successivi refresh della pagina.
    """
    init_db()


def main():
    # 1. Configurazione Pagina (Deve essere la prima istruzione Streamlit)
    st.set_page_config(
        page_title="FuelPyTracker",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Inizializzazione Database (Idempotente)
    initialize_app()

    # 3. Sidebar di Navigazione
    st.sidebar.title("Navigazione")
    
    # Definiamo le opzioni del menu
    options = {
        "Dashboard": views.render_dashboard,
        "Rifornimenti": views.render_fuel_page,
        "Manutenzione": views.render_maintenance_page
    }
    
    # Widget di selezione
    selected_page = st.sidebar.radio("Vai a:", list(options.keys()))

    # 4. Routing (Mostra la funzione associata alla pagina selezionata)
    # Esegue la funzione corrispondente (es. views.render_dashboard())
    options[selected_page]()

    # Footer nella sidebar
    st.sidebar.markdown("---")
    st.sidebar.text("FuelPyTracker v0.1")

if __name__ == "__main__":
    main()