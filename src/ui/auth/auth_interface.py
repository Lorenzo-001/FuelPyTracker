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

# --- CALLBACKS (Business Logic) ---
# Queste funzioni vengono eseguite PRIMA del rendering della UI,
# garantendo che lo stato (st.session_state.user) sia aggiornato
# quando main.py riparte.

def login_callback():
    """Gestisce l'azione di login triggerata dal form."""
    email = st.session_state.get("login_email", "")
    password = st.session_state.get("login_pass", "")
    
    if not email or not password:
        st.session_state.auth_error = "Dati mancanti."
        return

    try:
        res = sign_in(email, password)
        if res.user:
            st.session_state.user = res.user
            st.session_state.auth_error = None
            # Il rerun è implicito dopo la callback
    except Exception:
        st.session_state.auth_error = "Credenziali non valide."

def register_callback():
    """Gestisce l'azione di registrazione triggerata dal form."""
    new_email = st.session_state.get("reg_email", "")
    new_pass = st.session_state.get("reg_pass", "")
    confirm_pass = st.session_state.get("reg_pass_conf", "")

    if new_pass != confirm_pass:
        st.session_state.auth_error = "Le password non coincidono."
        return
    
    try:
        res = sign_up(new_email, new_pass)
        if res.user:
            st.session_state.user = res.user
            st.session_state.auth_error = None
    except Exception as e:
        msg = str(e)
        if "User already registered" in msg:
            st.session_state.auth_error = "Email già registrata."
        else:
            st.session_state.auth_error = f"Errore registrazione: {msg}"

# --- COMPONENTI INTERNI ---

def _render_login_form():
    """Renderizza il form di accesso."""
    with st.form("login_form", border=False):
        # Keys necessarie per il binding con le callback
        st.text_input("Email", key="login_email", placeholder="nome@esempio.com")
        st.text_input("Password", type="password", key="login_pass", placeholder="••••••")
        
        st.markdown('<div style="height: 5px;"></div>', unsafe_allow_html=True)
        
        # Gestione Errori Feedback
        if st.session_state.get("auth_error"):
            st.error(st.session_state.auth_error)
            st.session_state.auth_error = None # Reset dopo visualizzazione

        # Submit con Callback
        st.form_submit_button(
            "Entra", 
            width='stretch', 
            type="primary",
            on_click=login_callback # Hook logica
        )

def _render_register_form():
    """Renderizza il form di registrazione."""
    with st.form("register_form", border=False):
        st.text_input("Email", key="reg_email")
        st.text_input("Password (min 6)", key="reg_pass", type="password")
        st.text_input("Conferma Password", key="reg_pass_conf", type="password")
        
        st.markdown('<div style="height: 5px;"></div>', unsafe_allow_html=True)

        if st.session_state.get("auth_error"):
             st.error(st.session_state.auth_error)
             st.session_state.auth_error = None

        st.form_submit_button(
            "Crea Account", 
            width='stretch',
            on_click=register_callback # Hook logica
        )

# --- INTERFACCIA PUBBLICA ---

def render_login_interface():
    """Renderizza l'intera pagina di autenticazione (Login/Register)."""
    apply_login_css()
    render_login_header()
    
    tab_login, tab_register = st.tabs(["🔐 Accedi", "📝 Registrati"])
    
    with tab_login:
        _render_login_form()
        # Pulsante esterno al form per evitare submit accidentali
        if st.button("Password dimenticata?", key="forgot_pass_btn", type="tertiary"):
             st.session_state.reset_password_mode = True # Flag per switch pagina
             st.rerun()

    with tab_register:
        _render_register_form()