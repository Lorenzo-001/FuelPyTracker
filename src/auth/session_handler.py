import streamlit as st
import extra_streamlit_components as stx
from src.services.auth.auth_service import get_client
import time

# Costanti per i cookie
COOKIE_ACCESS_TOKEN = "sb_access_token"
COOKIE_REFRESH_TOKEN = "sb_refresh_token"
COOKIE_EXPIRY_DAYS = 30



# 2. Manager Cookies con Key stabile
# Non usiamo st.cache_resource perché genera CachedWidgetWarning con i widget custom.
# Usiamo invece una key fissa per garantire che Streamlit non ricrei l'iframe a ogni run.
def get_cookie_manager():
    return stx.CookieManager(key="auth_cookie_manager")

def init_session():
    """
    Tenta di ripristinare la sessione dai cookie.
    Gestisce la race condition del caricamento cookie con un doppio passaggio soft.
    """
    # 1. Se l'utente è già autenticato, usciamo subito
    if st.session_state.get("user") is not None:
        return

    # 2. Inizializziamo il manager (che deve essere renderizzato per funzionare)
    cookie_manager = get_cookie_manager()
    cookies = cookie_manager.get_all()

    # 3. Gestione Sincronizzazione Cookie (Race Condition Fix)
    # Stx torna {} di default finché il frontend non risponde. 
    # Dobbiamo distinguere tra "veramente vuoto" e "non ancora caricato".
    
    # Usiamo un flag in session_state per sapere se abbiamo già fatto un "wait cycle"
    if "cookie_sync_attempted" not in st.session_state:
        st.session_state.cookie_sync_attempted = False

    # Se i cookie sono vuoti E non abbiamo ancora atteso la sincronizzazione...
    if not cookies and not st.session_state.cookie_sync_attempted:
        # Diamo tempo al componente di montarsi e rispondere
        time.sleep(0.15) 
        cookies = cookie_manager.get_all()
        
        # Se ancora vuoti, forziamo UN solo rerun per assicurarci che il frontend abbia processato
        if not cookies:
            st.session_state.cookie_sync_attempted = True # Marchiamo come tentato
            st.rerun()
            return

    # Analisi Cookie (Sia che siano arrivati subito, sia dopo il sync)
    access_token = cookies.get(COOKIE_ACCESS_TOKEN)
    refresh_token = cookies.get(COOKIE_REFRESH_TOKEN)

    if access_token and refresh_token:
        try:
            client = get_client()
            # Ripristina sessione
            # Nota: set_session valida anche il token. Se scaduto lancia eccezione.
            response = client.auth.set_session(access_token, refresh_token)
            if response.user:
                st.session_state.user = response.user
                # Reset del flag per eventuali refresh futuri puliti
                st.session_state.cookie_sync_attempted = False
        except Exception as e:
            # Token invalido o scaduto -> Pulizia
            # Non chiamiamo clear_session() che fa rerun, ma puliamo e basta per mostrare il login
            print(f"Session restore failed: {e}")
            st.session_state.user = None
    else:
        # Nessun cookie trovato (utente nuovo o sloggato) -> Login standard
        pass

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
