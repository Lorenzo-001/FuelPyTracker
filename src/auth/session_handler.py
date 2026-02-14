import streamlit as st
# import extra_streamlit_components as stx # RIMOSSO: Non serve più per la scrittura/lettura
from src.services.auth.auth_service import get_client

# Costanti per i cookie
COOKIE_MANAGER_KEY = "auth_cookie_manager"
COOKIE_ACCESS_TOKEN = "sb_access_token"
COOKIE_REFRESH_TOKEN = "sb_refresh_token"
COOKIE_EXPIRY_DAYS = 30

def init_session():
    """
    Tenta di ripristinare la sessione dai cookie.
    Usa st.context.cookies (nativo) per la lettura sincrona e immediata.
    """
    # 1. Se siamo già autenticati, usciamo subito
    if st.session_state.get("user") is not None:
        return

    # 2. Lettura Sincrona dei Cookie (Nativo Streamlit >= 1.39)
    # st.context.cookies è un dizionario disponibile fin dall'avvio dello script.
    # Non richiede rendering di componenti o iframe.
    try:
        cookies = st.context.cookies
    except AttributeError:
        # Fallback per versioni vecchie (non dovremmo essere qui se usiamo 1.51)
        cookies = {}

    # 3. Analisi e Ripristino
    access_token = cookies.get(COOKIE_ACCESS_TOKEN)
    refresh_token = cookies.get(COOKIE_REFRESH_TOKEN)

    if access_token and refresh_token:
        try:
            client = get_client()
            # Ripristina sessione Supabase
            # set_session valida automaticamente i token
            response = client.auth.set_session(access_token, refresh_token)
            
            if response.user:
                st.session_state.user = response.user
                # Opzionale: Se il token è stato rinfrescato, potremmo volerlo aggiornare nei cookie
                # Ma richiederebbe stx che è lento. Per ora ci fidiamo del fatto che
                # Supabase gestirà il prossimo refresh o che il cookie scadrà tra 30gg.
                # Se servisse, si potrebbe chiamare save_session(response.session) qui,
                # ma attenzione che save_session RICHIEDE il rendering del componente.
                
                # Rerun NON necessario se siamo all'inizio dello script, 
                # ma utile per aggiornare la UI se siamo in un flusso intermedio.
                # In main.py init_session è chiamato prima di tutto, quindi la UI
                # si renderizzerà corretta subito dopo.
                pass 

        except Exception as e:
            print(f"Session restore failed: {e}")
            # Token invalido -> Logout pulito
            st.session_state.user = None
            # Non proviamo a cancellare i cookie qui per non invocare stx
            # (che romperebbe il flusso sincrono). Se il login fallisce,
            # l'utente vedrà la schermata di login e potrà ri-loggarsi,
            # sovrascrivendo i cookie vecchi.
    else:
        # Nessun token trovato -> Restiamo sloggati
        pass

    # Nota: NON inizializziamo get_cookie_manager() qui.
    # Lo faremo solo se e quando dovremo scrivere (login) o cancellare (logout).
    # Questo evita iframe inutili in tutte le pagine dove l'utente naviga solo.

import streamlit.components.v1 as components

def save_session(session):
    """
    Salva i token della sessione nei cookie usando JS Injection.
    Questo metodo è sincrono rispetto al rendering HTML e più affidabile di stx.
    Da chiamare PRIMA di un eventuale st.rerun().
    """
    if not session:
        return

    # Calcolo scadenza in secondi
    max_age = COOKIE_EXPIRY_DAYS * 24 * 60 * 60
    
    # Costruzione Script JS
    # Nota: path=/ è fondamentale per rendere il cookie visibile in tutta l'app
    js_script = f"""
    <script>
        document.cookie = "{COOKIE_ACCESS_TOKEN}={session.access_token}; path=/; max-age={max_age}; SameSite=Lax";
        document.cookie = "{COOKIE_REFRESH_TOKEN}={session.refresh_token}; path=/; max-age={max_age}; SameSite=Lax";
    </script>
    """
    
    # Iniezione invisibile
    components.html(js_script, height=0, width=0)

def clear_session():
    """
    Rimuove i cookie e i dati di sessione (Logout).
    """
    # 1. Cancellazione Cookie via JS (Set max-age=0)
    js_script = f"""
    <script>
        document.cookie = "{COOKIE_ACCESS_TOKEN}=; path=/; max-age=0";
        document.cookie = "{COOKIE_REFRESH_TOKEN}=; path=/; max-age=0";
    </script>
    """
    components.html(js_script, height=0, width=0)
        
    # 2. Logout da Supabase
    try:
        get_client().auth.sign_out()
    except:
        pass
        
    # 3. Pulisci session state
    st.session_state.user = None