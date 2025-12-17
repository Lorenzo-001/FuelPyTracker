import streamlit as st
from supabase import create_client, Client

# 1. Inizializzazione Client Supabase
# Legge URL e KEY direttamente dai secrets di Streamlit
# Usa @st.cache_resource per non riconnettersi a ogni click
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = get_supabase_client()

# 2. Funzioni di Autenticazione

def sign_in(email, password):
    """Esegue il Login. Ritorna l'oggetto sessione o lancia errore."""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email, 
            "password": password
        })
        return response
    except Exception as e:
        # Ritorna l'errore puro per gestirlo nella UI
        raise e

def sign_up(email, password):
    """Registra un nuovo utente."""
    try:
        response = supabase.auth.sign_up({
            "email": email, 
            "password": password
        })
        return response
    except Exception as e:
        raise e

def sign_out():
    """Effettua il Logout."""
    supabase.auth.sign_out()

def get_current_user():
    """
    Recupera l'utente dalla sessione attiva.
    Utile per verificare se il token è ancora valido.
    """
    session = supabase.auth.get_session()
    if session:
        return session.user
    return None

def update_user_password_secure(email, old_password, new_password):
    """
    Aggiorna la password verificando prima che la vecchia sia corretta.
    Gestisce l'errore di password identica traducendolo.
    """
    # 1. Verifica Vecchia Password (tentativo di login)
    try:
        supabase.auth.sign_in_with_password({
            "email": email, 
            "password": old_password
        })
    except Exception:
        return False, "La password attuale inserita non è corretta."

    # 2. Tentativo Aggiornamento Password
    try:
        attributes = {"password": new_password}
        supabase.auth.update_user(attributes)
        return True, "Password aggiornata con successo!"
        
    except Exception as e:
        err_msg = str(e)
        # 3. Traduzione Errore Specifico Supabase
        if "New password should be different from the old password" in err_msg:
            return False, "Errore: La nuova password deve essere diversa dalla precedente."
        return False, f"Errore imprevisto: {err_msg}"
    
def update_user_email(new_email):
    """
    Richiede il cambio email. 
    Nota: Supabase invierà una mail di conferma al nuovo indirizzo (e spesso anche al vecchio).
    L'aggiornamento effettivo avviene solo dopo il click sul link.
    """
    try:
        attributes = {"email": new_email}
        supabase.auth.update_user(attributes)
        return True, "Richiesta inviata! Controlla la tua posta (sia vecchia che nuova) per confermare il cambio."
    except Exception as e:
        return False, str(e)