import streamlit as st
from src.services.auth.auth_service import get_client

# --- COSTANTI ---
QP_ACCESS_TOKEN  = "sb_at"
QP_REFRESH_TOKEN = "sb_rt"


# ---------------------------------------------------------------------------
# STRATEGIA: URL-based session persistence
#
# I cookie browser NON possono essere scritti in modo affidabile da Streamlit
# (st.markdown non esegue <script>, components.html usa blob URL cross-origin).
#
# Soluzione: il refresh_token (30 giorni) vive nei query_params dell'URL.
# Il browser preserva l'URL completo al refresh (F5), quindi i token sono
# sempre disponibili. Ad ogni ciclo, Supabase rinnova l'access_token se scaduto.
# ---------------------------------------------------------------------------


def save_session(session):
    """
    Dopo il login: salva i token nei query_params (relay post-callback).
    Al prossimo ciclo Streamlit, init_session() li legge e ripristina la sessione.
    """
    if not session:
        return
    st.query_params[QP_ACCESS_TOKEN]  = session.access_token
    st.query_params[QP_REFRESH_TOKEN] = session.refresh_token

# Alias per compatibilità
stage_session = save_session


def init_session():
    """
    Ripristina la sessione dai query_params.

    Se i token sono validi: sessione ripristinata, QP aggiornati con i token
    eventualmente rinfrescati da Supabase (così il refresh_token non scade mai).

    Se i token sono invalidi/scaduti: QP puliti, utente torna al login.
    """
    if st.session_state.get("user") is not None:
        return

    qp_at = st.query_params.get(QP_ACCESS_TOKEN)
    qp_rt = st.query_params.get(QP_REFRESH_TOKEN)

    if not (qp_at and qp_rt):
        return  # Nessun token nell'URL → schermata di login

    try:
        response = get_client().auth.set_session(qp_at, qp_rt)

        if response and response.user:
            st.session_state.user = response.user

            # Aggiorna i token nell'URL con quelli rinfrescati da Supabase
            # (l'access_token dura 1h, il refresh_token si rinnova ad ogni uso)
            sess = getattr(response, "session", None)
            new_at = getattr(sess, "access_token",  None) if sess else None
            new_rt = getattr(sess, "refresh_token", None) if sess else None

            st.query_params[QP_ACCESS_TOKEN]  = new_at or qp_at
            st.query_params[QP_REFRESH_TOKEN] = new_rt or qp_rt

    except Exception as e:
        print(f"[FuelPyTracker] Session restore failed: {e}")
        st.session_state.user = None
        # Token non validi: rimuoviamo dall'URL per tornare al login
        st.query_params.pop(QP_ACCESS_TOKEN,  None)
        st.query_params.pop(QP_REFRESH_TOKEN, None)


def clear_session():
    """
    Logout: rimuove i token dall'URL, fa sign-out da Supabase, azzera lo stato.
    """
    st.query_params.pop(QP_ACCESS_TOKEN,  None)
    st.query_params.pop(QP_REFRESH_TOKEN, None)
    try:
        get_client().auth.sign_out()
    except Exception:
        pass
    st.session_state.user = None