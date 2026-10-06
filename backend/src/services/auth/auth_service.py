import os
import logging
# pyrefly: ignore [missing-import]
from supabase import create_client, Client

from src.database.url import is_local_sqlite
from src.demo import is_demo_mode

logger = logging.getLogger(__name__)


def _get_supabase_credentials() -> tuple[str | None, str | None]:
    """Recupera URL e Key di Supabase dalle variabili d'ambiente OS."""
    url = os.environ.get("SUPABASE_URL", "").strip() or None
    key = os.environ.get("SUPABASE_KEY", "").strip() or None
    return url, key


# 1. Inizializzazione Client Supabase
def get_client() -> Client | None:
    """
    Recupera o crea il client Supabase.
    Con LOCAL_SQLITE + demo non serve Supabase.
    """
    if is_local_sqlite() and is_demo_mode():
        return None

    url, key = _get_supabase_credentials()
    if url and key:
        return create_client(url, key)
    return None


def is_supabase_configured() -> bool:
    """Restituisce True solo se le credenziali Supabase (URL e KEY) sono configurate."""
    url, key = _get_supabase_credentials()
    return bool(url and key)


# 2. Funzioni di Autenticazione

def sign_in(email: str, password: str):
    """Esegue il Login. Ritorna l'oggetto sessione o lancia errore."""
    client = get_client()
    if client is None:
        raise RuntimeError("Client Supabase non configurato (credenziali mancanti).")
    return client.auth.sign_in_with_password({
        "email": email,
        "password": password
    })


def sign_up(email: str, password: str):
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
    if not client:
        return None

    session = client.auth.get_session()
    if session:
        return session.user
    return None


def update_user_password_secure(email: str, old_password: str, new_password: str):
    """
    Aggiorna la password verificando prima che la vecchia sia corretta.
    Gestisce l'errore di password identica traducendolo.
    Usa un client temporaneo per la verifica per non corrompere la sessione attiva.
    """
    url, key = _get_supabase_credentials()
    if not url or not key:
        return False, "Credenziali Supabase non configurate."

    # Client usa-e-getta per verificare le credenziali senza invalidare la sessione attiva.
    try:
        temp_client = create_client(url, key)
        temp_client.auth.sign_in_with_password({
            "email": email,
            "password": old_password
        })
    except Exception:
        return False, "La password attuale inserita non è corretta."

    # Vecchia password verificata: aggiorna via client principale.
    try:
        attributes = {"password": new_password}
        main_client = get_client()
        if not main_client:
            return False, "Client Supabase non disponibile."
        main_client.auth.update_user(attributes)
        return True, "Password aggiornata con successo!"
    except Exception as e:
        err_msg = str(e)
        if "New password should be different from the old password" in err_msg:
            return False, "Errore: La nuova password deve essere diversa dalla precedente."
        return False, f"Errore imprevisto: {err_msg}"


def update_user_email(new_email: str):
    """
    Richiede il cambio email.
    Nota: Supabase invierà una mail di conferma al nuovo indirizzo (e una notifica al vecchio).
    L'aggiornamento effettivo avviene solo dopo il click sul link.
    """
    client = get_client()
    if not client:
        return False, "Client Supabase non disponibile."

    try:
        attributes = {"email": new_email}
        client.auth.update_user(attributes)
        return True, "Richiesta inviata! Controlla la tua posta (sia vecchia che nuova) per confermare il cambio."
    except Exception as e:
        return False, str(e)


def send_password_reset_email(email: str):
    """Invia la mail di recupero password con redirect verso la nuova rotta frontend /reset-password."""
    client = get_client()
    if not client:
        return False, "Client Supabase non configurato."

    try:
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173").rstrip("/")
        redirect_url = f"{frontend_url}/reset-password"

        client.auth.reset_password_email(email, options={
            "redirect_to": redirect_url
        })
        return True, "Email di recupero inviata! Controlla la tua casella di posta."
    except Exception as e:
        return False, str(e)


def exchange_code_for_session(auth_code: str):
    """
    Scambia il codice PKCE per una sessione utente attiva.
    """
    client = get_client()
    if not client:
        return False, "Client Supabase non configurato."
    try:
        res = client.auth.exchange_code_for_session({"auth_code": auth_code})
        return True, res.user
    except Exception as e:
        return False, str(e)


def update_password_head(new_password: str):
    """
    Aggiorna la password SENZA chiedere la vecchia.
    Da usare SOLO nel flusso di recupero password (quando l'utente è loggato via link email).
    """
    client = get_client()
    if not client:
        return False, "Client Supabase non configurato."
    try:
        attributes = {"password": new_password}
        client.auth.update_user(attributes)
        return True, "Password impostata con successo!"
    except Exception as e:
        err_msg = str(e)
        if "New password should be different from the old password" in err_msg:
            return False, "La nuova password deve essere diversa da quella precedente."
        return False, str(e)


def set_session_from_url(access_token: str, refresh_token: str):
    """
    Ripristina una sessione utente partendo dai token raw (Implicit Flow).
    Usato quando il link di reset password contiene #access_token invece di ?code.
    """
    client = get_client()
    if not client:
        return False, "Client Supabase non configurato."
    try:
        res = client.auth.set_session(access_token, refresh_token)
        return True, res.user
    except Exception as e:
        return False, str(e)