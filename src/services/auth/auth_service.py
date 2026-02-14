import streamlit as st
from supabase import create_client, Client

# 1. Inizializzazione Client Supabase (SESSION ISOLATED)
def get_client() -> Client:
    """
    Recupera o crea il client Supabase per la sessione corrente.
    Assicura che ogni utente abbia la propria istanza isolata.
    """
    if "supabase_client" not in st.session_state:
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            st.session_state.supabase_client = create_client(url, key)
        except Exception as e:
            st.error(f"Errore configurazione Supabase: {e}")
            return None
            
    return st.session_state.supabase_client

# 2. Funzioni di Autenticazione

def sign_in(email, password):
    """Esegue il Login. Ritorna l'oggetto sessione o lancia errore."""
    try:
        response = get_client().auth.sign_in_with_password({
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
        response = get_client().auth.sign_up({
            "email": email, 
            "password": password
        })
        return response
    except Exception as e:
        raise e

def sign_out():
    """Effettua il Logout."""
    get_client().auth.sign_out()

def get_current_user():
    """
    Recupera l'utente dalla sessione attiva.
    Utile per verificare se il token è ancora valido.
    """
    client = get_client()
    if not client: return None
    
    session = client.auth.get_session()
    if session:
        return session.user
    return None

def update_user_password_secure(email, old_password, new_password):
    """
    Aggiorna la password verificando prima che la vecchia sia corretta.
    Gestisce l'errore di password identica traducendolo.
    Usa un client temporaneo per la verifica per non corrompere la sessione attiva.
    """
    # 1. Creiamo un client 'Disposable' (Usa e Getta) solo per verificare le credenziali
    # Se il login fallisce qui, non invalidiamo la sessione dell'utente nell'app principale.
    try:
        temp_url = st.secrets["supabase"]["url"]
        temp_key = st.secrets["supabase"]["key"]
        temp_client = create_client(temp_url, temp_key)
        
        # Tentativo di login sul client temporaneo
        temp_client.auth.sign_in_with_password({
            "email": email, 
            "password": old_password
        })
    except Exception:
        return False, "La password attuale inserita non è corretta."

    # 2. Se siamo qui, la vecchia password è corretta.
    # Usiamo il client PRINCIPALE (che ha la sessione attiva) per fare l'update.
    try:
        attributes = {"password": new_password}
        get_client().auth.update_user(attributes)
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
        get_client().auth.update_user(attributes)
        return True, "Richiesta inviata! Controlla la tua posta (sia vecchia che nuova) per confermare il cambio."
    except Exception as e:
        return False, str(e)
    
def send_password_reset_email(email):
    """Invia la mail di recupero password."""
    try:
        # Recupera l'URL dai secrets. 
        # Se non c'è nel TOML, usa localhost come fallback di default.
        redirect_url = st.secrets["supabase"].get("redirect_url", "http://localhost:8501")
        
        get_client().auth.reset_password_email(email, options={
            "redirect_to": redirect_url
        })
        return True, "Email di recupero inviata! Controlla la tua casella di posta."
    except Exception as e:
        return False, str(e)

def exchange_code_for_session(auth_code):
    """
    Scambia il codice PKCE (proveniente dall'URL) per una sessione utente attiva.
    Questo logga automaticamente l'utente.
    """
    try:
        res = get_client().auth.exchange_code_for_session({"auth_code": auth_code})
        return True, res.user
    except Exception as e:
        return False, str(e)
    
def update_password_head(new_password):
    """
    Aggiorna la password SENZA chiedere la vecchia.
    Da usare SOLO nel flusso di recupero password (quando l'utente è loggato via link email).
    """
    try:
        attributes = {"password": new_password}
        get_client().auth.update_user(attributes)
        return True, "Password impostata con successo!"
    except Exception as e:
        err_msg = str(e)
        if "New password should be different from the old password" in err_msg:
            return False, "La nuova password deve essere diversa da quella precedente."
        
        return False, str(e)
    
def set_session_from_url(access_token, refresh_token):
    """
    Ripristina una sessione utente partendo dai token raw (Implicit Flow).
    Usato quando il link di reset password contiene #access_token invece di ?code.
    """
    try:
        # Imposta manualmente la sessione nel client Supabase
        res = get_client().auth.set_session(access_token, refresh_token)
        return True, res.user
    except Exception as e:
        return False, str(e)