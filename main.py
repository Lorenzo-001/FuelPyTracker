import sys
import os
import streamlit as st

# 1. Configurazione Path Assoluti
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.database.core import init_db
from src.ui.pages import dashboard, fuel, maintenance, settings, profile
from src.services.auth import get_current_user, sign_out
from src.ui.auth.auth_interface import render_login_interface

@st.cache_resource
def initialize_app():
    """Inizializzazione una-tantum (DB Cache)."""
    init_db()

# --- CALLBACKS CORRETTE PER LA NAVIGAZIONE COORDINATA ---
def update_nav_main():
    """
    Quando clicco sul menu Principale:
    1. Aggiorno la pagina corrente.
    2. Imposto a None il menu Account (lo deseleziono visivamente).
    """
    st.session_state.current_page = st.session_state.nav_radio_main
    st.session_state.nav_radio_account = None 

def update_nav_account():
    """
    Quando clicco sul menu Account:
    1. Aggiorno la pagina corrente.
    2. Imposto a None il menu Principale (lo deseleziono visivamente).
    """
    st.session_state.current_page = st.session_state.nav_radio_account
    st.session_state.nav_radio_main = None

def main():
    # 2. Configurazione Pagina
    st.set_page_config(
        page_title="FuelPyTracker",
        page_icon="⛽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS HACK: Rende i bottoni "primary" rossi solo nella sidebar (Logout)
    st.markdown("""
        <style>
            div[data-testid="stSidebar"] button[kind="primary"] {
                background-color: #FF4B4B; border-color: #FF4B4B; color: white;
            }
            div[data-testid="stSidebar"] button[kind="primary"]:hover {
                background-color: #D93636; border-color: #D93636;
            }
        </style>
    """, unsafe_allow_html=True)

    # 3. Init App
    initialize_app()

    # 4. SECURITY GATE
    current_user = get_current_user()

    if not current_user:
        render_login_interface()
        return
    
    st.session_state['user'] = current_user

    # 5. GESTIONE NAVIGAZIONE (SIDEBAR DOPPIA)
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    # Definiamo le pagine disponibili
    pages_main = {
        "Dashboard": dashboard.render,
        "Rifornimenti": fuel.render,
        "Manutenzione": maintenance.render,
        "Impostazioni": settings.render
    }
    
    pages_account = {
        "Profilo": profile.render
    }

    # Uniamo tutto per il routing finale
    all_pages = {**pages_main, **pages_account}

    with st.sidebar:
        # Header Utente
        c1, c2 = st.columns([1, 4])
        with c1: st.write("👤")
        with c2: 
            st.caption("Loggato come:")
            st.markdown(f"**{current_user.email.split('@')[0]}**")
        
        st.divider()
        
        # --- BLOCCO NAVIGAZIONE PRINCIPALE ---
        st.title("Navigazione")
        
        # Calcoliamo l'indice
        idx_main = list(pages_main.keys()).index(st.session_state.current_page) if st.session_state.current_page in pages_main else None
        
        st.radio(
            "Vai a:", 
            list(pages_main.keys()), 
            index=idx_main, 
            key="nav_radio_main",
            label_visibility="collapsed",
            on_change=update_nav_main  # Chiama la funzione corretta
        )

        st.write("") 

        # --- BLOCCO ACCOUNT ---
        st.title("Account")
        
        # Calcoliamo l'indice
        idx_acc = list(pages_account.keys()).index(st.session_state.current_page) if st.session_state.current_page in pages_account else None

        st.radio(
            "Account:",
            list(pages_account.keys()), 
            index=idx_acc,
            key="nav_radio_account",
            label_visibility="collapsed",
            on_change=update_nav_account # Chiama la funzione corretta
        )

        st.write("")
        st.divider()
        
        # Bottone Logout (Rosso)
        if st.button("Esci (Logout)", type="primary", use_container_width=True):
            sign_out()
            # Pulizia stato sessione al logout
            for key in ['current_page', 'nav_radio_main', 'nav_radio_account', 'user']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        st.markdown("---")
        st.caption("FuelPyTracker v2.0")

    # 6. ROUTING E RENDERING
    if st.session_state.current_page in all_pages:
        all_pages[st.session_state.current_page]()
    else:
        dashboard.render()

if __name__ == "__main__":
    main()