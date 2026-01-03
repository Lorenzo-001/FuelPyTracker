import streamlit as st
import time
from src.services.auth.auth_service import *
from gotrue.errors import AuthApiError

# --- FUNZIONE MODALE PER IL RESET ---
@st.dialog("Recupero Password")
def render_reset_modal():
    st.write("Inserisci la tua email. Ti invieremo un link per reimpostare la password.")
    email_reset = st.text_input("La tua email", key="reset_email_input")
    
    if st.button("Invia Link di Recupero", type="primary", width='stretch'):
        if not email_reset:
            st.warning("Inserisci un indirizzo email valido.")
        else:
            ok, msg = send_password_reset_email(email_reset)
            if ok:
                st.success(msg)
                time.sleep(2)
                st.rerun() # Chiude il modale dopo il successo
            else:
                st.error(f"Errore: {msg}")

def render_login_interface():
    """
    Gestisce l'intera UI di autenticazione.
    Ritorna True se il login ha successo, False altrimenti.
    """
    
    # CSS Custom per trasformare il bottone "tertiary" in un link piccolo e carino
    st.markdown("""
        <style>
            /* Target specifico per i bottoni 'tertiary' nella sidebar o colonne */
            button[kind="tertiary"] {
                color: #78909c !important; /* Grigio-Azzurro */
                text-decoration: underline;
                font-size: 0.45rem !important; /* Testo più piccolo */
                border: none !important;
                background: transparent !important;
                padding: 0 !important;
                margin-top: -10px !important; /* Avvicina un po' al form */
                justify-content: flex-start !important; /* Allinea a sinistra */
                height: auto !important;
            }
            button[kind="tertiary"]:hover {
                color: #4a6fa5 !important; /* Diventa più blu al passaggio */
                text-decoration: none;
            }
            button[kind="tertiary"]:focus {
                color: #4a6fa5 !important;
                box-shadow: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Layout a colonne    
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("⛽ FuelPyTracker")
        st.markdown("##### Il tuo diario di bordo digitale")
        st.divider()

        # Tabs per scambiare tra Login e Registrazione
        tab_login, tab_register = st.tabs(["🔐 Accedi", "📝 Registrati"])

        # --- TAB LOGIN ---
        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="nome@esempio.com")
                password = st.text_input("Password", type="password", placeholder="••••••")
                
                submit = st.form_submit_button("Entra", width='stretch', type="primary")
                
                if submit:
                    if not email or not password:
                        st.warning("Inserisci email e password.")
                    else:
                        try:
                            res = sign_in(email, password)
                            if res.user:
                                st.success("Login effettuato! 🚀")
                                time.sleep(0.5)
                                st.rerun() # Ricarica l'app per mostrare la dashboard
                        except Exception as e:
                            st.error(f"Errore di accesso: Credenziali non valide o utente non trovato.")

            # --- LINK DISCRETO PER PASSWORD DIMENTICATA ---
            # Un bottone 'tertiary' o 'secondary' sembra un link testuale
            if st.button("Password dimenticata?", type="tertiary", width='stretch'):
                    render_reset_modal()

        # --- TAB REGISTRAZIONE ---
        with tab_register:
            with st.form("register_form"):
                st.write("Crea un nuovo account")
                new_email = st.text_input("Email Registrazione")
                new_pass = st.text_input("Password (min 6 car.)", type="password")
                confirm_pass = st.text_input("Conferma Password", type="password")
                
                btn_register = st.form_submit_button("Crea Account", width='stretch')
                
                if btn_register:
                    if new_pass != confirm_pass:
                        st.error("Le password non coincidono.")
                    elif len(new_pass) < 6:
                        st.error("Minimo 6 caratteri.")
                    else:
                        try:
                            # Poiché "Confirm Email" è OFF su Supabase, 
                            # sign_up esegue il login automatico.
                            res = sign_up(new_email, new_pass)
                            
                            if res.user:
                                st.success("✅ Registrazione completata! Accesso in corso...")
                                time.sleep(1)
                                st.rerun()
                                
                        except AuthApiError as api_err:
                            if "User already registered" in str(api_err):
                                st.error("Email già registrata. Vai su 'Accedi'.")
                            else:
                                st.error(f"Errore API: {api_err}")
                        except Exception as e:
                            st.error(f"Errore: {e}")