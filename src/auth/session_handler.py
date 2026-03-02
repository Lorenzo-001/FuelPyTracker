import streamlit as st
from datetime import datetime, timedelta
from src.services.auth.auth_service import get_client

# --- COSTANTI ---
COOKIE_ACCESS_TOKEN  = "sb_access_token"
COOKIE_REFRESH_TOKEN = "sb_refresh_token"
COOKIE_EXPIRY_DAYS   = 30
QP_ACCESS_TOKEN      = "sb_at"   # Query param key (breve per sicurezza)
QP_REFRESH_TOKEN     = "sb_rt"


# ---------------------------------------------------------------------------
# COOKIE MANAGER
# ---------------------------------------------------------------------------
# Usiamo extra_streamlit_components.CookieManager perché:
# - components.v1.html() usa iframe con blob URL (origine "null")
# - window.parent.document.cookie lancia SecurityError cross-origin (silenzioso)
# - st.markdown() NON esegue <script> (React dangerouslySetInnerHTML)
# - CookieManager è servito dall'origine dell'app → document.cookie funziona
#
# Nota: il CookieManager ha una latenza di 1 rerun sul primo caricamento.
# Al primo refresh il login potrebbe lampeggiare brevemente, poi la sessione
# viene ripristinata al rerun successivo (automatico).
# ---------------------------------------------------------------------------

def _get_cm():
    """Ritorna il CookieManager singleton per questo ciclo di render."""
    import extra_streamlit_components as stx
    return stx.CookieManager(key="__session_cm__")


# ---------------------------------------------------------------------------
# SAVE / STAGE SESSION (Relay sincrono via query_params)
# ---------------------------------------------------------------------------

def save_session(session):
    """
    Salva i token nel relay sincrono (st.query_params) subito dopo il login.

    Perché query_params?
    - È SERVER‑SIDE: disponibile già al prossimo ciclo Streamlit, senza JS.
    - Elimina la race condition dell'approccio iframe + time.sleep().

    I token vengono letti da init_session() al ciclo successivo e
    convertiti in cookie persistenti tramite CookieManager.
    """
    if not session:
        return
    st.query_params[QP_ACCESS_TOKEN]  = session.access_token
    st.query_params[QP_REFRESH_TOKEN] = session.refresh_token

# Alias per compatibilità con altri moduli
stage_session = save_session


# ---------------------------------------------------------------------------
# INIT SESSION (chiamata all'inizio di ogni ciclo in main.py)
# ---------------------------------------------------------------------------

def init_session():
    """
    Ripristina la sessione utente all'avvio di ogni ciclo Streamlit.

    Priorità:
      1. session_state.user già presente → niente da fare
      2. Token in st.query_params → relay post-login → scrivi cookie, pulisci QP
      3. Token in cookie (CookieManager) → restore da sessione precedente
    """
    if st.session_state.get("user") is not None:
        return

    cm = _get_cm()

    # --- CASO 1: Token nel relay (query_params) ---
    qp_at = st.query_params.get(QP_ACCESS_TOKEN)
    qp_rt = st.query_params.get(QP_REFRESH_TOKEN)

    if qp_at and qp_rt:
        try:
            response = get_client().auth.set_session(qp_at, qp_rt)
            if response.user:
                st.session_state.user = response.user
                # Ricava i token (eventualmente rinfrescati da Supabase)
                sess = response.session
                at = getattr(sess, "access_token",  None) or qp_at
                rt = getattr(sess, "refresh_token", None) or qp_rt
                # Scrivi cookie persistenti tramite CookieManager
                exp = datetime.now() + timedelta(days=COOKIE_EXPIRY_DAYS)
                cm.set(COOKIE_ACCESS_TOKEN,  at, expires_at=exp, key="__set_at__")
                cm.set(COOKIE_REFRESH_TOKEN, rt, expires_at=exp, key="__set_rt__")
        except Exception as e:
            print(f"[FuelPyTracker] QP session restore failed: {e}")
            st.session_state.user = None
        finally:
            # Pulizia relay: rimuoviamo i token dall'URL per sicurezza
            st.query_params.pop(QP_ACCESS_TOKEN,  None)
            st.query_params.pop(QP_REFRESH_TOKEN, None)
        return

    # --- CASO 2: Token nei cookie (restore da refresh browser) ---
    # Nota: al primo refresh dopo un nuovo deploy, cm.get() potrebbe restituire
    # None perché il componente non ha ancora inviato i valori. Streamlit fa un
    # rerun automatico e al ciclo successivo i cookie sono disponibili.
    cookie_at = cm.get(COOKIE_ACCESS_TOKEN)
    cookie_rt = cm.get(COOKIE_REFRESH_TOKEN)

    if cookie_at and cookie_rt:
        try:
            response = get_client().auth.set_session(cookie_at, cookie_rt)
            if response.user:
                st.session_state.user = response.user
        except Exception as e:
            print(f"[FuelPyTracker] Cookie session restore failed: {e}")
            st.session_state.user = None


# ---------------------------------------------------------------------------
# CLEAR SESSION (Logout)
# ---------------------------------------------------------------------------

def clear_session():
    """
    Logout completo: cancella cookie, fa sign-out da Supabase, azzera session_state.
    """
    cm = _get_cm()
    try:
        cm.delete(COOKIE_ACCESS_TOKEN,  key="__del_at__")
    except Exception:
        pass
    try:
        cm.delete(COOKIE_REFRESH_TOKEN, key="__del_rt__")
    except Exception:
        pass
    try:
        get_client().auth.sign_out()
    except Exception:
        pass
    st.session_state.user = None