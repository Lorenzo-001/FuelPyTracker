import streamlit as st
import time
from src.services.auth.auth_service import update_password_head

def render_reset_page():
    """Renderizza la pagina forzata di cambio password."""
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.header("🔐 Ripristino Password")
        st.markdown("Hai richiesto il reset della password. Inseriscine una nuova per continuare.")
        
        with st.container(border=True):
            with st.form("new_password_force_form"):
                new_p = st.text_input("Nuova Password", type="password", placeholder="Minimo 6 caratteri")
                conf_p = st.text_input("Conferma Password", type="password", placeholder="Ripeti password")
                
                if st.form_submit_button("Salva e Accedi", type="primary", use_container_width=True):
                    if new_p != conf_p:
                        st.error("Le password non coincidono.")
                    elif len(new_p) < 6:
                        st.error("Minimo 6 caratteri.")
                    else:
                        res, msg = update_password_head(new_p)
                        if res:
                            _render_success_card()
                        else:
                            st.error(f"Errore: {msg}")

def _render_success_card():
    st.markdown("""
        <div style="background-color: #d1fae5; border: 1px solid #34d399; padding: 15px; border-radius: 8px; text-align: center; margin-top: 10px; color: #065f46;">
            <h3 style="margin: 0; font-size: 18px;">✅ Password Aggiornata!</h3>
            <p style="margin: 5px 0 0 0; font-size: 14px;">Reindirizzamento alla dashboard...</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.session_state["reset_password_mode"] = False
    st.session_state["current_page"] = "Dashboard"
    time.sleep(2)
    st.rerun()