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


def update_user_password_secure(email: str, old_password: str, new_password: str) -> tuple[bool, str]:
    """
    Aggiorna la password verificando prima che la vecchia sia corretta.
    Usa un client isolato usa-e-getta autenticato con la vecchia password per non corrompere altre sessioni.
    """
    url, key = _get_supabase_credentials()
    if not url or not key:
        return False, "Credenziali Supabase non configurate."

    try:
        temp_client = create_client(url, key)
        auth_res = temp_client.auth.sign_in_with_password({
            "email": email,
            "password": old_password
        })
        if not auth_res or not auth_res.user:
            return False, "La password attuale inserita non è corretta."
    except Exception:
        return False, "La password attuale inserita non è corretta."

    # Vecchia password verificata: aggiorna sul client appena autenticato
    try:
        temp_client.auth.update_user({"password": new_password})
        return True, "Password aggiornata con successo!"
    except Exception as e:
        err_msg = str(e)
        if "New password should be different from the old password" in err_msg:
            return False, "La nuova password deve essere diversa dalla precedente."
        return False, f"Errore durante l'aggiornamento della password: {err_msg}"


def update_user_email(new_email: str, user_token: str | None = None) -> tuple[bool, str]:
    """
    Richiede il cambio email.
    Supabase invierà un'email di conferma al nuovo indirizzo (e notifica al vecchio).
    """
    url, key = _get_supabase_credentials()
    if not url or not key:
        return False, "Credenziali Supabase non configurate."

    try:
        temp_client = create_client(url, key)
        if user_token:
            temp_client.auth._request(
                "PUT",
                "user",
                body={"email": new_email},
                jwt=user_token,
            )
        else:
            main_client = get_client()
            if not main_client:
                return False, "Client Supabase non disponibile."
            main_client.auth.update_user({"email": new_email})
        return True, "Richiesta inviata! Controlla la tua casella di posta per confermare l'indirizzo."
    except Exception as e:
        logger.warning("Errore cambio email in %s: %s", new_email, e)
        return False, f"Impossibile aggiornare l'email: {e}"


def send_password_reset_email(email: str) -> tuple[bool, str]:
    """Invia la mail di recupero password con redirect verso la rotta frontend /reset-password."""
    client = get_client()
    if not client:
        return False, "Client Supabase non configurato."

    try:
        from src.api.config import FRONTEND_URL
        frontend_url = FRONTEND_URL
    except Exception:
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173").rstrip("/")

    redirect_url = f"{frontend_url}/reset-password"

    try:
        client.auth.reset_password_email(email, options={
            "redirect_to": redirect_url
        })
        return True, "Email di recupero inviata! Controlla la tua casella di posta."
    except Exception as e:
        logger.warning("Errore invio email recupero per %s: %s", email, e)
        return False, str(e)


def update_password_with_recovery_token(
    access_token: str,
    new_password: str,
    refresh_token: str | None = None,
) -> tuple[bool, str]:
    """
    Aggiorna la password dell'utente utilizzando il Bearer access_token ricevuto
    dal link di recupero email di Supabase Auth.
    Usa un client isolato con sessione associata al token.
    """
    url, key = _get_supabase_credentials()
    if not url or not key:
        return False, "Credenziali Supabase non configurate."

    try:
        temp_client = create_client(url, key)
        if refresh_token:
            try:
                temp_client.auth.set_session(access_token, refresh_token)
                temp_client.auth.update_user({"password": new_password})
                return True, "Password aggiornata con successo!"
            except Exception as e_session:
                logger.debug("set_session non riuscito, tento chiamata diretta con bearer: %s", e_session)

        # Chiamata diretta con Bearer token su endpoint Supabase Auth /user
        temp_client.auth._request(
            "PUT",
            "user",
            body={"password": new_password},
            jwt=access_token,
        )
        return True, "Password aggiornata con successo!"
    except Exception as exc:
        err_msg = str(exc)
        logger.warning("Fallimento aggiornamento password via recovery token: %s", exc)
        if "New password should be different from the old password" in err_msg:
            return False, "La nuova password deve essere diversa da quella precedente."
        if any(w in err_msg.lower() for w in ["invalid", "expired", "jwt", "unauthorized", "token"]):
            return False, "Il link di recupero è scaduto o non è valido. Richiedi un nuovo link."
        return False, f"Impossibile aggiornare la password: {err_msg}"


def exchange_code_for_session(auth_code: str):
    """Scambia il codice PKCE per una sessione utente attiva."""
    client = get_client()
    if not client:
        return False, "Client Supabase non configurato."
    try:
        res = client.auth.exchange_code_for_session({"auth_code": auth_code})
        return True, res.user
    except Exception as e:
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