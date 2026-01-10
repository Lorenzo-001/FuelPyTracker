import sys
import os
import streamlit as st
# 1. Configurazione Path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.database.core import init_db
from src.ui.pages import dashboard, fuel, maintenance, settings, profile
from src.ui.auth.auth_interface import render_login_interface
from src.services.auth.auth_service import get_current_user
from src.ui.assets.styles import inject_js_bridge, apply_custom_css
from src.services.auth.router import handle_auth_redirects
from src.ui.components.sidebar import render_sidebar
from src.ui.auth.reset_page import render_reset_page

@st.cache_resource
def initialize_app():
    """Inizializzazione DB e Risorse."""
    init_db()

def main():    
    # 1. Iniezione Stili e JS Bridge
    inject_js_bridge()
    apply_custom_css()
    
    # 2. Init Applicazione
    initialize_app()

    # 3. Gestione Routing Auth (Magic Link)
    handle_auth_redirects()

    # 4. Modalità Reset Password (Bloccante)
    if st.session_state.get("reset_password_mode", False):
        render_reset_page()
        return

    # 5. Security Gate
    current_user = st.session_state.get("user") or get_current_user()
    
    if not current_user:
        render_login_interface()
        return
    
    # Persistenza utente
    st.session_state['user'] = current_user

    # 6. Mappa Pagine
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

    pages_main = {
        "Dashboard": dashboard.render,
        "Rifornimenti": fuel.render,
        "Manutenzione": maintenance.render,
        "Impostazioni": settings.render
    }
    pages_account = { "Profilo": profile.render }
    all_pages = {**pages_main, **pages_account}

    # 7. Render Sidebar e Navigazione
    render_sidebar(current_user, pages_main, pages_account)

    # 8. Render Pagina Corrente
    if st.session_state.current_page in all_pages:
        all_pages[st.session_state.current_page]()
    else:
        dashboard.render()

if __name__ == "__main__":
    main()