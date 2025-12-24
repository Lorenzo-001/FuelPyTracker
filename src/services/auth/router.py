import streamlit as st
from src.services.auth.auth_service import exchange_code_for_session, set_session_from_url

def handle_auth_redirects():
    """
    Gestisce l'intercettazione dei token di auth dall'URL.
    Restituisce True se un recupero password è avvenuto con successo.
    """
    query_params = st.query_params
    success = False
    error_msg = None

    # Caso 1: Flusso PKCE
    if "code" in query_params:
        auth_code = query_params["code"]
        ok, res = exchange_code_for_session(auth_code)
        if ok:
            success = True
            st.session_state['user'] = res # Imposta utente temporaneo
        else:
            error_msg = res

    # Caso 2: Flusso Implicit (Token)
    elif "access_token" in query_params:
        access_token = query_params["access_token"]
        refresh_token = query_params.get("refresh_token")
        flow_type = query_params.get("type", "recovery")
        
        ok, res = set_session_from_url(access_token, refresh_token)
        if ok:
            success = True
            st.session_state['user'] = res
            if flow_type == "recovery":
                st.session_state["reset_password_mode"] = True
        else:
            error_msg = res

    if success:
        st.toast("✅ Accesso recuperato! Caricamento...", icon="🔐")
        st.query_params.clear()
        st.rerun()
    
    if error_msg:
        st.error(f"⚠️ Link non valido o scaduto: {error_msg}")
        if st.button("Torna alla Login"):
            st.query_params.clear()
            st.rerun()
        st.stop() # Blocca l'esecuzione qui