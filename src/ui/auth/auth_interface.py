import streamlit as st
import time
from src.services.auth.auth_service import sign_in, sign_up, send_password_reset_email
from gotrue.errors import AuthApiError
from src.ui.assets.styles import apply_login_css, render_login_header

# --- FUNZIONE MODALE PER IL RESET ---
@st.dialog("Recupero Password")
def render_reset_modal():
    st.write("Inserisci la tua email. Ti invieremo un link.")
    email_reset = st.text_input("La tua email", key="reset_email_input")
    
    if st.button("Invia Link", type="primary", width='stretch'):
        if not email_reset:
            st.warning("Email richiesta.")
        else:
            try:
                ok, msg = send_password_reset_email(email_reset)
                if ok:
                    st.success("Link inviato!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Errore: {msg}")
            except Exception as e:
                st.error(f"Errore: {e}")

# --- COMPONENTI INTERNI ---

def _render_login_form():
    """Gestisce il form di login."""
    with st.form("login_form", border=False):
        email = st.text_input("Email", placeholder="nome@esempio.com")
        password = st.text_input("Password", type="password", placeholder="••••••")
        
        # Spacer
        st.markdown('<div style="height: 5px;"></div>', unsafe_allow_html=True)
        
        submit = st.form_submit_button("Entra", width='stretch', type="primary")
        
        if submit:
            if not email or not password:
                st.warning("Dati mancanti.")
            else:
                try:
                    res = sign_in(email, password)
                    if res.user:
                        st.success("Accesso effettuato!")
                        time.sleep(0.5)
                        st.rerun()
                except Exception:
                    st.error("Credenziali non valide.")

def _render_register_form():
    """Gestisce il form di registrazione."""
    with st.form("register_form", border=False):
        new_email = st.text_input("Email")
        new_pass = st.text_input("Password (min 6)")
        confirm_pass = st.text_input("Conferma Password", type="password")
        
        st.markdown('<div style="height: 5px;"></div>', unsafe_allow_html=True)
        
        btn_register = st.form_submit_button("Crea Account", width='stretch')
        
        if btn_register:
            if new_pass != confirm_pass:
                st.error("Le password non coincidono.")
            elif len(new_pass) < 6:
                st.error("Minimo 6 caratteri.")
            else:
                try:
                    res = sign_up(new_email, new_pass)
                    if res.user:
                        st.success("Registrato! Accesso...")
                        time.sleep(1)
                        st.rerun()
                except AuthApiError as api_err:
                    if "User already registered" in str(api_err):
                        st.error("Email già presente.")
                    else:
                        st.error(f"Errore: {api_err}")
                except Exception as e:
                    st.error(f"Errore: {e}")

# --- INTERFACCIA PRINCIPALE ---

def render_login_interface():
    """
    Interfaccia di Login Mobile-First ultra compatta.
    """
    # 1. Applica CSS
    apply_login_css()
    
    # 2. Renderizza Header
    render_login_header()

    # 3. Tabs per Login/Registrazione
    tab_login, tab_register = st.tabs(["🔐 Accedi", "📝 Registrati"])

    with tab_login:
        _render_login_form()
        # Link Password Dimenticata
        if st.button("Password dimenticata?", type="tertiary", width='stretch'):
            render_reset_modal()

    with tab_register:
        _render_register_form()