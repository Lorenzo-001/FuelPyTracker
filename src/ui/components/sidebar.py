import streamlit as st
import os
from datetime import date
from sqlalchemy import or_
from src.services.auth.auth_service import sign_out
from src.assets.styles import apply_sidebar_css
from src.database.core import get_db
from src.database import crud

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

def _check_urgent_deadlines(user_id):
    """
    Verifica scadenze scadute (ROSSO) e mostra warning nella sidebar.
    """
    try:
        # Apriamo una sessione veloce solo per il check
        db = next(get_db())
        
        # 1. Recupera dati necessari
        max_km = crud.get_max_km(db, user_id)
        today = date.today()
        
        # 2. Query maintenance con scadenze impostate
        active_m = db.query(crud.Maintenance).filter(
            crud.Maintenance.user_id == user_id,
            or_(crud.Maintenance.expiry_km != None, crud.Maintenance.expiry_date != None)
        ).all()
        
        expired_count = 0
        for m in active_m:
            is_exp_km = (m.expiry_km is not None and m.expiry_km < max_km)
            is_exp_date = (m.expiry_date is not None and m.expiry_date < today)
            
            if is_exp_km or is_exp_date:
                expired_count += 1
        
        db.close()
        
        # 3. Visualizza Warning se necessario
        if expired_count > 0:
            st.warning(f"**{expired_count} Scadenze Passate!**")
            # Pulsante rapido per andare alla pagina (aggiorna lo stato della nav)
            if st.button("Vai a Scadenze", key="sidebar_warn_btn", type="primary", width='stretch'):
                st.session_state.current_page = "Manutenzione"
                st.session_state.nav_radio_main = "Manutenzione" # Sincronizza il radio button
                st.session_state.nav_radio_account = None
                st.rerun()
            st.divider()
            
    except Exception:
        pass # Fail-safe per non rompere la sidebar in caso di errori DB

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

        # --- 2.5 WARNING SYSTEM ---
        _check_urgent_deadlines(current_user.id)

        # --- 3. FOOTER ---
                
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