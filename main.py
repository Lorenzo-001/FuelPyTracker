import sys
import os
import streamlit as st
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.database.core import init_db
from src.ui.pages import dashboard, fuel, maintenance, settings, profile
from src.ui.auth.auth_interface import render_login_interface
from src.services.auth.auth_service import get_current_user
from src.ui.assets.styles import inject_js_bridge, apply_custom_css
from src.services.auth.router import handle_auth_redirects
from src.ui.components.sidebar import render_sidebar
from src.ui.auth.reset_page import render_reset_page

# --- 1. CONFIGURAZIONE INIZIALE ASSOLUTA ---
st.set_page_config(
    page_title="FuelPyTracker",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="collapsed" 
)

@st.cache_resource
def initialize_app():
    """Inizializzazione una-tantum del database."""
    init_db()

def main():
    # --- 2. INIT SERVIZI BACKEND ---
    initialize_app()
    handle_auth_redirects()     # Gestione Magic Link (Email)
    inject_js_bridge()          # Helper JS per UX
    
    # --- 3. GESTIONE STATO UTENTE (Headless) ---
    # Recuperiamo l'utente PRIMA di disegnare qualsiasi cosa
    if "user" not in st.session_state:
        st.session_state.user = get_current_user()

    # --- 4. CSS STATE CONTROL (Anti-Flicker) ---
    # Nascondiamo la sidebar via CSS se non siamo loggati.
    # Questo previene che appaia vuota o "fluttui" durante il caricamento del login.
    if not st.session_state.user:
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {display: none;}
                [data-testid="stSidebarCollapsedControl"] {display: none;}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        # Applica stili globali app (solo quando loggato)
        apply_custom_css()

    # --- 5. GESTIONE RESET PASSWORD ---
    # Modalità esclusiva bloccante
    if st.session_state.get("reset_password_mode", False):
        render_reset_page()
        return

    # --- 6. MASTER RENDERING SLOT ---
    # Pattern "Single Slot": Creiamo un contenitore vuoto che fungerà da
    # unico punto di ingresso per il Login, evitando sovrapposizioni.
    master_slot = st.empty()

    # SCENARIO A: UTENTE NON LOGGATO -> LOGIN
    if not st.session_state.user:
        with master_slot.container():
            render_login_interface()
        return

    # SCENARIO B: UTENTE LOGGATO -> DASHBOARD
    # 1. Pulizia Slot: Rimuoviamo il login (o residui) dallo slot master
    master_slot.empty()
    
    # 2. Setup Routing
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    pages_main = {
        "Dashboard": dashboard.render,
        "Rifornimenti": fuel.render,
        "Manutenzione": maintenance.render,
        "Impostazioni": settings.render
    }
    pages_account = { "Profilo": profile.render }
    
    # 3. Render Sidebar (Navigazione)
    render_sidebar(st.session_state.user, pages_main, pages_account)

    # 4. Render Contenuto Pagina
    # Scriviamo direttamente nel flusso principale (fuori da master_slot)
    # per garantire il corretto funzionamento di layout e scrolling.
    page_name = st.session_state.current_page
    all_pages = {**pages_main, **pages_account}
    
    if page_name in all_pages:
        all_pages[page_name]()
    else:
        dashboard.render()

if __name__ == "__main__":
    main()