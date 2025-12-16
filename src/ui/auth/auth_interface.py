import streamlit as st
import time
from src.services.auth import sign_in, sign_up

def render_login_interface():
    """
    Gestisce l'intera UI di autenticazione.
    Ritorna True se il login ha successo, False altrimenti.
    """
    
    # Layout a colonne per centrare il box (responsive)
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
                
                submit = st.form_submit_button("Entra", use_container_width=True, type="primary")
                
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

        # --- TAB REGISTRAZIONE ---
        with tab_register:
            with st.form("register_form"):
                new_email = st.text_input("Email")
                new_pass = st.text_input("Password (min 6 car.)", type="password")
                confirm_pass = st.text_input("Conferma Password", type="password")
                
                btn_register = st.form_submit_button("Crea Account", use_container_width=True)
                
                if btn_register:
                    if new_pass != confirm_pass:
                        st.error("Le password non coincidono.")
                    elif len(new_pass) < 6:
                        st.error("La password deve essere di almeno 6 caratteri.")
                    else:
                        try:
                            res = sign_up(new_email, new_pass)
                            # Controllo user
                            user = getattr(res, 'user', None) or (res if hasattr(res, 'id') else None)
                            
                            if user:
                                st.success("Account creato con successo! Ora puoi accedere dalla tab 'Accedi'.")
                            else:
                                st.info("Controlla la tua email per confermare la registrazione.")
                        except Exception as e:
                            st.error(f"Errore registrazione: {e}")