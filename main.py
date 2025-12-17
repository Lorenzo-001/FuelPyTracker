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

# --- CALLBACKS ---
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
    
    # CSS GLOBALE (Sidebar Logout Rosso + Stile Card Utente)
    st.markdown("""
        <style>
            /* Bottone Logout Rosso */
            div[data-testid="stSidebar"] button[kind="primary"] {
                background-color: #FF4B4B; border-color: #FF4B4B; color: white;
            }
            div[data-testid="stSidebar"] button[kind="primary"]:hover {
                background-color: #D93636; border-color: #D93636;
            }
            
            /* Stile Card Utente Sidebar */
            .sidebar-user-card {
                background-color: #262730; /* Darker background per card */
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #444;
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 20px;
            }
            .sidebar-user-avatar {
                width: 40px; height: 40px;
                background-color: #FF4B4B;
                color: white;
                border-radius: 6px; /* Quadrato stondato */
                display: flex; justify-content: center; align-items: center;
                font-size: 20px; font-weight: bold;
            }
            .sidebar-user-info {
                display: flex; flex-direction: column;
            }
            .sidebar-user-name {
                font-weight: bold; font-size: 0.95rem; color: white;
            }
            .sidebar-user-role {
                font-size: 0.75rem; color: #aaa;
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
        # --- CARD UTENTE STYLIZZATA ---
        # Estraiamo l'iniziale per l'avatar
        user_email = current_user.email
        initial = user_email[0].upper() if user_email else "?"
        short_email = user_email.split('@')[0]

        st.markdown(f"""
            <div class="sidebar-user-card">
                <div class="sidebar-user-avatar">{initial}</div>
                <div class="sidebar-user-info">
                    <span class="sidebar-user-name">{short_email}</span>
                    <span class="sidebar-user-role">Utente Standard</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # --- BLOCCO NAVIGAZIONE PRINCIPALE ---
        st.title("Navigazione")
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