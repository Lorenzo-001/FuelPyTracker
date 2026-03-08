import sys
import os
import streamlit as st

from src.ui.components.dashboard import dashboard
from src.ui.components.fuel import fuel
from src.ui.components.maintenance import maintenance
from src.ui.components.profile import profile
from src.database.core import init_db
from src.ui.components.settings import settings
from src.auth.auth_interface import render_login_interface
from src.auth.session_handler import init_session
from src.assets.styles import inject_js_bridge, apply_custom_css
from src.services.auth.router import handle_auth_redirects
from src.ui.components.sidebar import render_sidebar
from src.auth.reset_page import render_reset_page
from src.demo import is_demo_mode, DEMO_USER



sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

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
    if "user" not in st.session_state:
        st.session_state.user = None
        
    init_session()

    # --- 4. DEMO MODE: Bypass autenticazione ---
    if is_demo_mode() and not st.session_state.get("user"):
        st.session_state.user = DEMO_USER
        st.rerun()  # Forza un re-run pulito con la sessione già valorizzata

    # --- 5. CSS STATE CONTROL (Anti-Flicker) ---
    # Nascondiamo la sidebar via CSS se non siamo loggati.
    # Questo previene che appaia vuota o "fluttui" durante il caricamento del login.
    if not st.session_state.get("user"):
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
    # Inizializzazione chiavi di navigazione sidebar: deve avvenire qui (una volta sola)
    # per evitare il warning "widget created with default but also set via Session State API".
    if "nav_radio_main" not in st.session_state:
        st.session_state.nav_radio_main = st.session_state.current_page
    if "nav_radio_account" not in st.session_state:
        st.session_state.nav_radio_account = None

    pages_main = {
        "Dashboard": dashboard.render,
        "Rifornimenti": fuel.render,
        "Manutenzione": maintenance.render,
        "Impostazioni": settings.render
    }
    pages_account = { "Profilo": profile.render }
    
    # 3. Render Sidebar (Navigazione)
    render_sidebar(st.session_state.get("user"), pages_main, pages_account)

    if is_demo_mode():
        st.info("👀 Benvenuto nella Demo Pubblica! Per garantire un'esperienza ottimale a tutti, l'applicazione è in modalità Sola Lettura. L'aggiunta e la modifica dei dati sono disabilitate.")

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