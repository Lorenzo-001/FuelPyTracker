import streamlit as st
from src.services.auth.auth_service import sign_out

def render_sidebar(current_user, pages_main, pages_account):
    """Renderizza la sidebar con card utente e menu di navigazione."""
    
    with st.sidebar:
        # Card Utente
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
        
        # Menu Principale
        st.title("Navigazione")
        
        # Callback per gestire lo stato
        def _update_nav_main():
            st.session_state.current_page = st.session_state.nav_radio_main
            st.session_state.nav_radio_account = None 

        idx_main = list(pages_main.keys()).index(st.session_state.current_page) if st.session_state.current_page in pages_main else None
        st.radio("Vai a:", list(pages_main.keys()), index=idx_main, key="nav_radio_main", label_visibility="collapsed", on_change=_update_nav_main)

        st.write("") 

        # Menu Account
        st.title("Account")
        
        def _update_nav_account():
            st.session_state.current_page = st.session_state.nav_radio_account
            st.session_state.nav_radio_main = None

        idx_acc = list(pages_account.keys()).index(st.session_state.current_page) if st.session_state.current_page in pages_account else None
        st.radio("Account:", list(pages_account.keys()), index=idx_acc, key="nav_radio_account", label_visibility="collapsed", on_change=_update_nav_account)

        st.write("")
        st.divider()
        
        # Logout
        if st.button("Esci (Logout)", type="primary", width='stretch'):
            sign_out()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")
        st.caption("FuelPyTracker v2.0")