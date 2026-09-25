import os
from pathlib import Path
import toml
# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
from supabase import create_client, Client

from src.database.url import is_local_sqlite
from src.demo import is_demo_mode


def _get_supabase_credentials() -> tuple[str | None, str | None]:
    """Recupera URL e Key di Supabase da env, st.secrets o file secrets.toml."""
    url = os.environ.get("SUPABASE_URL", "").strip() or None
    key = os.environ.get("SUPABASE_KEY", "").strip() or None
    if url and key:
        return url, key

    # Prova da st.secrets se disponibile
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        if url and key:
            return str(url), str(key)
    except Exception:
        pass

    # Prova da file secrets.toml locale
    try:
        candidates = [
            Path(__file__).resolve().parents[3] / ".streamlit" / "secrets.toml",
            Path.cwd() / "backend" / ".streamlit" / "secrets.toml",
            Path.cwd() / ".streamlit" / "secrets.toml",
        ]
        for c in candidates:
            if c.is_file():
                data = toml.load(c)
                sub = data.get("supabase", {})
                if sub.get("url") and sub.get("key"):
                    return str(sub["url"]), str(sub["key"])
    except Exception:
        pass

    return None, None


# 1. Inizializzazione Client Supabase (SESSION ISOLATED)
def get_client() -> Client | None:
    """
    Recupera o crea il client Supabase.
    In Streamlit isola la sessione via st.session_state; fuori da Streamlit crea il client autonomo.
    Con LOCAL_SQLITE + demo non serve Supabase (niente secrets).
    """
    if is_local_sqlite() and is_demo_mode():
        return None

    # Se Streamlit è attivo con session_state
    try:
        if hasattr(st, "session_state"):
            if "supabase_client" not in st.session_state:
                url, key = _get_supabase_credentials()
                if not url or not key:
                    st.error("Errore configurazione Supabase: credenziali mancanti")
                    return None
                st.session_state.supabase_client = create_client(url, key)
            return st.session_state.supabase_client
    except Exception:
        pass

    # Fuori da Streamlit (FastAPI / CLI / Worker)
    url, key = _get_supabase_credentials()
    if url and key:
        return create_client(url, key)
    return None


def is_supabase_configured() -> bool:
    """Restituisce True solo se le credenziali Supabase (URL e KEY) sono configurate."""
    url, key = _get_supabase_credentials()
    return bool(url and key)


# 2. Funzioni di Autenticazione

def sign_in(email, password):
    """Esegue il Login. Ritorna l'oggetto sessione o lancia errore."""
    client = get_client()
    if client is None:
        raise RuntimeError("Client Supabase non configurato (credenziali mancanti).")
    return client.auth.sign_in_with_password({
        "email": email, 
        "password": password
    })


def sign_up(email, password):
    """Registra un nuovo utente."""
    client = get_client()
    if client is None:
        raise RuntimeError("Client Supabase non configurato (credenziali mancanti).")
    return client.auth.sign_up({
        "email": email, 
        "password": password
    })


def sign_out():
    """Effettua il Logout."""
    client = get_client()
    if client is None:
        return
    client.auth.sign_out()

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
    # Client usa-e-getta per verificare le credenziali senza invalidare la sessione attiva.
    try:
        temp_url = st.secrets["supabase"]["url"]
        temp_key = st.secrets["supabase"]["key"]
        temp_client = create_client(temp_url, temp_key)
        temp_client.auth.sign_in_with_password({
            "email": email, 
            "password": old_password
        })
    except Exception:
        return False, "La password attuale inserita non è corretta."

    # Vecchia password verificata: aggiorna via client principale (sessione attiva intatta).
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
        # Imposta la sessione nel client Supabase a partire dai token raw (Implicit Flow).
        res = get_client().auth.set_session(access_token, refresh_token)
        return True, res.user
    except Exception as e:
        return False, str(e)