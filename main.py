import sys
import os
import streamlit as st

# 1. Configurazione Path Assoluti
# Aggiunge la cartella corrente (src) al path per permettere import diretti (es. 'from database...')
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.database.core import init_db
from src.ui.pages import dashboard, fuel, maintenance, settings

# ### NUOVO: Importiamo i servizi di autenticazione
from src.services.auth import get_current_user, sign_out
from src.ui.auth.auth_interface import render_login_interface

@st.cache_resource
def initialize_app():
    """Inizializzazione una-tantum (DB Cache)."""
    init_db()

def main():
    # 2. Configurazione Pagina Streamlit
    # Nota: Manteniamo 'wide' come layout predefinito per la dashboard
    st.set_page_config(
        page_title="FuelPyTracker",
        page_icon="⛽",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 3. Bootstrapping Applicazione
    initialize_app()

    # 4. SECURITY GATE (Il "Portiere")
    # ---------------------------------------------------------
    # Controlliamo se c'è un utente loggato prima di mostrare qualsiasi cosa
    current_user = get_current_user()

    if not current_user:
        # CASO A: Utente NON loggato
        # Mostriamo solo l'interfaccia di Login e fermiamo l'esecuzione qui.
        render_login_interface()
        return  # <--- IMPORTANTE: Blocca il caricamento del resto dell'app
    
    # CASO B: Utente Loggato
    # Se arriviamo qui, l'utente esiste. Salviamolo in session_state per usarlo nelle pagine.
    st.session_state['user'] = current_user
    # ---------------------------------------------------------

    # 5. Costruzione Sidebar (Visibile solo se loggato)
    with st.sidebar:
        # ### NUOVO: Header Utente e Tasto Logout
        st.write(f"👤 **{current_user.email}**")
        if st.button("Esci (Logout)", key="logout_btn", use_container_width=True):
            sign_out()
            st.rerun() # Ricarica la pagina per tornare al login
        
        st.divider()
        st.title("Navigazione")
    
    # Mappatura delle pagine esistenti
    pages = {
        "Dashboard": dashboard.render,
        "Rifornimenti": fuel.render,
        "Manutenzione": maintenance.render,
        "Impostazioni": settings.render
    }
    
    # Menu di navigazione
    selection = st.sidebar.radio("Vai a:", list(pages.keys()))

    # 6. Routing e Rendering Pagina
    # Nota: Le pagine verranno renderizzate qui. 
    # Presto dovremo aggiornare le funzioni .render() per accettare 'current_user'
    # ma per ora le chiamiamo così, sapendo che useranno st.session_state['user']
    pages[selection]()

    st.sidebar.markdown("---")
    st.sidebar.text("FuelPyTracker v2.0-dev")

if __name__ == "__main__":
    main()