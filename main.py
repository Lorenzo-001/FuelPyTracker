import sys
import os
import streamlit as st

# 1. Configurazione Path Assoluti
# Aggiunge la cartella corrente (src) al path per permettere import diretti (es. 'from database...')
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.database.core import init_db
from src.ui.pages import dashboard, fuel, maintenance, settings

@st.cache_resource
def initialize_app():
    """Inizializzazione una-tantum (DB Cache)."""
    init_db()

def main():
    # 2. Configurazione Pagina Streamlit
    st.set_page_config(
        page_title="FuelPyTracker",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 3. Bootstrapping Applicazione
    initialize_app()

    # 4. Costruzione Sidebar
    st.sidebar.title("Navigazione")
    
    pages = {
        "Dashboard": dashboard.render,
        "Rifornimenti": fuel.render,
        "Manutenzione": maintenance.render,
        "Impostazioni": settings.render
    }
    
    selection = st.sidebar.radio("Vai a:", list(pages.keys()))

    # 5. Routing e Rendering Pagina
    pages[selection]()

    st.sidebar.markdown("---")
    st.sidebar.text("FuelPyTracker v1.0")

if __name__ == "__main__":
    main()