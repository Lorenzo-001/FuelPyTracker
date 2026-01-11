import streamlit as st
import os
from src.services.auth.auth_service import sign_out
from src.ui.assets.styles import apply_sidebar_css

def _render_user_profile(current_user):
    """Renderizza la card del profilo utente."""
    # Calcoliamo l'iniziale e puliamo il nome
    user_email = current_user.email if current_user.email else "Guest"
    short_name = user_email.split('@')[0]
    initial = short_name[0].upper() if short_name else "U"

    # HTML Strutturato con Flexbox (Avatar + Testo)
    st.markdown(f"""
        <div class="profile-container">
            <div class="profile-avatar">{initial}</div>
            <div class="profile-info">
                <span class="profile-name" title="{short_name}">{short_name}</span>
                <span class="profile-role">Account Standard</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar(current_user, pages_main, pages_account):
    """Renderizza la sidebar rifattorizzata con logo e stile premium."""
    
    # 1. Carica lo stile CSS personalizzato
    apply_sidebar_css()
    
    # Percorso del logo
    LOGO_PATH = "assets/logo.png" 

    with st.sidebar:
        # --- 1. LOGO ---
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width='stretch') # width='stretch' deprecated -> use_container_width
        else:
            # Fallback se non c'è il logo, magari un titolo testuale
            st.warning("Logo not found") 
            
        # --- 2. NAVIGAZIONE ---        
        # Callback per gestione stato menu mutuamente esclusivi
        def _update_nav_main():
            st.session_state.current_page = st.session_state.nav_radio_main
            st.session_state.nav_radio_account = None 

        def _update_nav_account():
            st.session_state.current_page = st.session_state.nav_radio_account
            st.session_state.nav_radio_main = None

        # Menu Principale
        st.markdown('<div class="nav-header">Navigazione</div>', unsafe_allow_html=True) # Titolo stilizzato custom invece di st.title
        idx_main = list(pages_main.keys()).index(st.session_state.current_page) if st.session_state.current_page in pages_main else None
        
        st.radio(
            "Main Menu", 
            list(pages_main.keys()), 
            index=idx_main, 
            key="nav_radio_main", 
            label_visibility="collapsed", 
            on_change=_update_nav_main
        )

        st.write("") 

        # Menu Account
        st.markdown('<div class="nav-header">Account</div>', unsafe_allow_html=True) # Titolo stilizzato custom
        idx_acc = list(pages_account.keys()).index(st.session_state.current_page) if st.session_state.current_page in pages_account else None
        
        st.radio(
            "Account Menu", 
            list(pages_account.keys()), 
            index=idx_acc, 
            key="nav_radio_account", 
            label_visibility="collapsed", 
            on_change=_update_nav_account
        )

        # --- 3. FOOTER ---
        st.divider()
        
        # Profilo Utente
        _render_user_profile(current_user)
        
        # Logout
        if st.button("Esci (Logout)", type="primary", width='stretch'): # width='stretch' deprecated
            sign_out()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.divider()

        # Versione
        st.markdown('<div class="version-footer">FuelPyTracker v2.0</div>', unsafe_allow_html=True)