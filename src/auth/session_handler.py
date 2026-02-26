import streamlit as st
from src.services.auth.auth_service import get_client

# --- COSTANTI ---
COOKIE_ACCESS_TOKEN  = "sb_access_token"
COOKIE_REFRESH_TOKEN = "sb_refresh_token"
COOKIE_EXPIRY_DAYS   = 30
QP_ACCESS_TOKEN      = "sb_at"   # Query param key (breve per sicurezza)
QP_REFRESH_TOKEN     = "sb_rt"


# ---------------------------------------------------------------------------
# SCRITTURA COOKIE (pagina padre, NON iframe)
# ---------------------------------------------------------------------------

def _write_cookies_js(access_token: str, refresh_token: str):
    """
    Scrive i cookie di sessione direttamente nella pagina Streamlit padre.

    Usa st.markdown() con unsafe_allow_html=True: il tag <script> viene
    iniettato nel DOM principale (non in un iframe), quindi l'esecuzione è
    immediata e sincrona rispetto al ciclo di rendering corrente.

    Aggiunge 'Secure' per garantire compatibilità con HTTPS e Safari mobile.
    La direttiva SameSite=Lax è compatibile con tutti i browser moderni.
    """
    max_age = COOKIE_EXPIRY_DAYS * 24 * 60 * 60

    # Costruiamo la stringa del cookie in modo sicuro
    # I token Supabase sono JWT standard (sicuri in URL/cookie)
    at = access_token.replace('"', '')
    rt = refresh_token.replace('"', '')

    cookie_flags = f"path=/; max-age={max_age}; SameSite=Lax; Secure"

    st.markdown(
        f"""
        <script>
            (function() {{
                document.cookie = "{COOKIE_ACCESS_TOKEN}={at}; {cookie_flags}";
                document.cookie = "{COOKIE_REFRESH_TOKEN}={rt}; {cookie_flags}";
                console.log("[FuelPyTracker] Cookie di sessione scritti con successo.");
            }})();
        </script>
        """,
        unsafe_allow_html=True,
    )


def _clear_cookies_js():
    """
    Cancella i cookie di sessione impostando max-age=0.
    Stessa tecnica di _write_cookies_js() — pagina padre, non iframe.
    """
    st.markdown(
        f"""
        <script>
            (function() {{
                document.cookie = "{COOKIE_ACCESS_TOKEN}=; path=/; max-age=0; SameSite=Lax; Secure";
                document.cookie = "{COOKIE_REFRESH_TOKEN}=; path=/; max-age=0; SameSite=Lax; Secure";
                console.log("[FuelPyTracker] Cookie di sessione rimossi.");
            }})();
        </script>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# STAGE (Salva token nei query_params — relay sincrono post-login)
# ---------------------------------------------------------------------------

def save_session(session):
    """
    Salva i token nel relay sincrono (st.query_params) subito dopo il login.

    Perché query_params e non cookie diretti?
    - st.query_params è SERVER-SIDE: il valore è disponibile già al prossimo
      ciclo di Streamlit, senza dipendere dall'esecuzione JS nel browser.
    - Elimina la race condition dell'approccio iframe + time.sleep().

    I token vengono letti e convertiti in cookie da init_session() al ciclo
    successivo (quando Streamlit fa il rerun post-callback).
    """
    if not session:
        return

    st.query_params[QP_ACCESS_TOKEN]  = session.access_token
    st.query_params[QP_REFRESH_TOKEN] = session.refresh_token

# Alias per compatibilità
stage_session = save_session


# ---------------------------------------------------------------------------
# INIT SESSION (chiamata all'inizio di ogni ciclo in main.py)
# ---------------------------------------------------------------------------

def init_session():
    """
    Ripristina la sessione utente all'avvio di ogni ciclo Streamlit.

    Priorità di ricerca dei token:
      1. Già loggato (st.session_state.user presente) → niente da fare
      2. Token in st.query_params → relay post-login → scrivi cookie, pulisci QP
      3. Token in st.context.cookies → restore da sessione precedente

    In entrambi i casi 2 e 3:
      - Chiama client.auth.set_session() per validare i token con Supabase
      - Imposta st.session_state.user
    """

    # --- GUARD: già autenticato ---
    if st.session_state.get("user") is not None:
        return

    # --- CASO 1: Token nel relay (query_params) ---
    # Arriva qui solo dopo un login con successo (stage_session ha scritto i QP)
    qp_at = st.query_params.get(QP_ACCESS_TOKEN)
    qp_rt = st.query_params.get(QP_REFRESH_TOKEN)

    if qp_at and qp_rt:
        try:
            client   = get_client()
            response = client.auth.set_session(qp_at, qp_rt)

            if response.user:
                st.session_state.user = response.user

                # Scrittura cookie persistenti nella pagina padre (sincrona)
                # Usiamo i token aggiornati restituiti da Supabase (potrebbero
                # essere stati rinfrescati durante set_session)
                new_session = response.session or response
                _write_cookies_js(
                    new_session.access_token if hasattr(new_session, "access_token") else qp_at,
                    new_session.refresh_token if hasattr(new_session, "refresh_token") else qp_rt,
                )

                # Pulizia relay: rimuoviamo i token dall'URL per sicurezza
                st.query_params.pop(QP_ACCESS_TOKEN, None)
                st.query_params.pop(QP_REFRESH_TOKEN, None)

        except Exception as e:
            print(f"[FuelPyTracker] Stage session restore failed: {e}")
            st.session_state.user = None
            # Pulizia in caso di errore
            st.query_params.pop(QP_ACCESS_TOKEN, None)
            st.query_params.pop(QP_REFRESH_TOKEN, None)

        return  # Usciamo: il cookie è stato scritto, al prossimo refresh useremo il caso 2

    # --- CASO 2: Token nei cookie (restore da refresh browser) ---
    try:
        cookies = st.context.cookies
    except AttributeError:
        cookies = {}

    cookie_at = cookies.get(COOKIE_ACCESS_TOKEN)
    cookie_rt = cookies.get(COOKIE_REFRESH_TOKEN)

    if cookie_at and cookie_rt:
        try:
            client   = get_client()
            response = client.auth.set_session(cookie_at, cookie_rt)

            if response.user:
                st.session_state.user = response.user
                # Aggiorniamo i cookie con i token eventualmente rinfrescati
                new_session = response.session or response
                if (hasattr(new_session, "access_token") and
                        new_session.access_token != cookie_at):
                    _write_cookies_js(
                        new_session.access_token,
                        new_session.refresh_token,
                    )

        except Exception as e:
            print(f"[FuelPyTracker] Cookie session restore failed: {e}")
            st.session_state.user = None


# ---------------------------------------------------------------------------
# CLEAR SESSION (Logout)
# ---------------------------------------------------------------------------

def clear_session():
    """
    Esegue il logout completo:
    1. Cancella i cookie via JS (pagina padre)
    2. Sign-out da Supabase
    3. Azzera la session_state
    """
    _clear_cookies_js()

    try:
        get_client().auth.sign_out()
    except Exception:
        pass

    st.session_state.user = None