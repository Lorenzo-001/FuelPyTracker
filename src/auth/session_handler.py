import streamlit as st
import extra_streamlit_components as stx
from src.services.auth.auth_service import get_client
import time

# Costanti per i cookie
COOKIE_ACCESS_TOKEN = "sb_access_token"
COOKIE_REFRESH_TOKEN = "sb_refresh_token"
COOKIE_EXPIRY_DAYS = 30


def get_cookie_manager():
    """
    Restituisce il manager dei cookie.
    Usa cache_resource per mantenere l'istanza unica e attiva.
    """
    return stx.CookieManager()

def init_session():
    """
    Tenta di ripristinare la sessione dai cookie se l'utente non è in session_state.
    Deve essere chiamato all'inizio di main.py.
    """
    if "user" not in st.session_state:
        st.session_state.user = None
        
    # Se l'utente è già loggato in memoria, non fare nulla
    if st.session_state.user:
        return

    # Tentativo di ripristino da Cookie
    cookie_manager = get_cookie_manager()
    # Nota: get_all() o get() potrebbero richiedere un rerun per essere letti al primo load
    # ma stx lo gestisce internamente di solito.
    
    # Attendiamo un attimo che il cookie manager sia pronto (hack comune con stx)
    # A volte serve un piccolo sleep o un check.
    cookies = cookie_manager.get_all()
    
    access_token = cookies.get(COOKIE_ACCESS_TOKEN)
    refresh_token = cookies.get(COOKIE_REFRESH_TOKEN)

    if access_token and refresh_token:
        try:
            client = get_client()
            # Ripristina la sessione su Supabase
            response = client.auth.set_session(access_token, refresh_token)
            if response.user:
                st.session_state.user = response.user
                # st.toast("Bentornato! Sessione ripristinata.", icon="🍪")
        except Exception as e:
            # Se il token è scaduto o invalido, puliamo tutto
            clear_session()
            print(f"Session restore failed: {e}")

def save_session(session):
    """
    Salva i token della sessione nei cookie.
    Da chiamare dopo un login avvenuto con successo.
    """
    if not session:
        return

    cookie_manager = get_cookie_manager()
    
    # Access Token
    cookie_manager.set(
        COOKIE_ACCESS_TOKEN, 
        session.access_token, 
        expires_at=datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS)
    )
    
    # Refresh Token
    if session.refresh_token:
        cookie_manager.set(
            COOKIE_REFRESH_TOKEN, 
            session.refresh_token, 
            expires_at=datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS)
        )

def clear_session():
    """
    Rimuove i cookie e i dati di sessione (Logout).
    """
    cookie_manager = get_cookie_manager()
    
    # Rimuovi cookie
    # Nota: stx.CookieManager delete a volte richiede il nome esatto
    try:
        cookie_manager.delete(COOKIE_ACCESS_TOKEN)
        cookie_manager.delete(COOKIE_REFRESH_TOKEN)
    except:
        pass
        
    # Logout da Supabase
    try:
        get_client().auth.sign_out()
    except:
        pass
        
    # Pulisci session state
    st.session_state.user = None
    
    # Rerun per aggiornare la UI
    # st.rerun() # Lasciamo che sia il chiamante a decidere se fare rerun

from datetime import datetime, timedelta
