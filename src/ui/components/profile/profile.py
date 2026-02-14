import streamlit as st
import time
from src.services.auth.auth_service import update_user_password_secure, update_user_email
from src.services.data.storage import upload_avatar, get_avatar_url
from src.ui.components.profile.kpi import _inject_custom_css

@st.fragment
def render():
    # 1. Inject Styles
    _inject_custom_css()
    
    st.header("👤 Profilo Utente")

    # 2. Setup Session & User Logic
    user = st.session_state["user"]

    if "avatar_version" not in st.session_state:
        st.session_state["avatar_version"] = int(time.time())
    
    # --- Gestione Date ---
    last_access_str = "N/A"
    created_at_str = "N/A"
    try:
        if user.last_sign_in_at:
            dt_last = user.last_sign_in_at if hasattr(user.last_sign_in_at, 'strftime') else None
            last_access_str = user.last_sign_in_at.strftime('%d/%m/%Y %H:%M') if dt_last else str(user.last_sign_in_at)[:10]

        if user.created_at:
            dt_created = user.created_at if hasattr(user.created_at, 'strftime') else None
            created_at_str = user.created_at.strftime('%d/%m/%Y') if dt_created else str(user.created_at)[:10]
    except Exception:
        pass

    # --- Avatar URL Logic ---
    avatar_url = get_avatar_url(user.id)
    if avatar_url:
        # Aggiunge timestamp per cache busting
        avatar_url = f"{avatar_url}?v={st.session_state['avatar_version']}"
    else:
        # Immagine di fallback se non esiste avatar
        avatar_url = "https://ui-avatars.com/api/?name=User&background=random&size=256"

    # =========================================================================
    # UI SECTION: Hero Card (HTML/CSS Custom Component)
    # =========================================================================
    
    # Costruiamo l'HTML iniettando le variabili Python
    # Nota: La classe 'user-email-title' ora gestisce la grandezza del font
    html_card = f"""
    <div class="profile-card">
        <div class="avatar-container">
            <img src="{avatar_url}" class="avatar-img" alt="Avatar">
        </div>
        <div class="user-info">
            <h4 class="user-email-title">{user.email}</h4>
            <div class="stats-container">
                <span class="stat-badge">🆔 {user.id}</span>
                <span class="stat-badge">📅 Iscritto: {created_at_str}</span>
                <span class="stat-badge">🕒 Ultimo: {last_access_str}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html_card, unsafe_allow_html=True)

    # =========================================================================
    # UI SECTION: Operations (Tabs)
    # =========================================================================
    
    tab_photo, tab_email, tab_security = st.tabs(["📷 Foto", "📧 Email", "🔐 Sicurezza"])

    # --- TAB 1: Upload Foto ---
    with tab_photo:
        st.caption("Aggiorna la tua immagine di profilo.")
        
        if "uploader_key" not in st.session_state:
            st.session_state["uploader_key"] = 0

        # File Uploader
        uploaded_file = st.file_uploader(
            "Scegli file", 
            type=['png', 'jpg', 'jpeg'],
            label_visibility="collapsed", 
            key=f"avatar_uploader_{st.session_state['uploader_key']}"
        )
        
        if uploaded_file is not None:
            with st.spinner("Caricamento in corso..."):
                new_url = upload_avatar(user.id, uploaded_file)
                
                if new_url:
                    st.toast("✅ Avatar aggiornato con successo!", icon="🎉")
                    time.sleep(1)
                    st.session_state["uploader_key"] += 1
                    st.session_state["avatar_version"] = int(time.time())
                    st.rerun()
                else:
                    st.error("Errore durante l'upload.")

    # --- TAB 2: Modifica Email ---
    with tab_email:
        st.info("Riceverai una mail di conferma al nuovo indirizzo.")
        
        with st.form("change_email_form", border=False):
            col_mail_1, col_mail_2 = st.columns([3, 1], vertical_alignment="bottom")
            with col_mail_1:
                new_email = st.text_input("Nuovo Indirizzo Email", placeholder="nuova@email.com")
            with col_mail_2:
                btn_email = st.form_submit_button("Invia", type="primary", width='stretch')
            
            if btn_email:
                if not new_email or "@" not in new_email:
                    st.error("Inserisci un'email valida.")
                elif new_email == user.email:
                    st.warning("Email identica all'attuale.")
                else:
                    success, msg = update_user_email(new_email)
                    if success:
                        st.success(msg)
                    else:
                        st.error(f"Errore: {msg}")

    # --- TAB 3: Sicurezza (Password) ---
    with tab_security:
        st.caption("È richiesta la password attuale per confermare le modifiche.")
        
        with st.form("change_pass_form_secure", border=True):
            old_pass = st.text_input("Password Attuale", type="password")
            st.divider()
            
            c1, c2 = st.columns(2)
            with c1:
                new_pass = st.text_input("Nuova Password", type="password")
            with c2:
                confirm_pass = st.text_input("Conferma Password", type="password")
            
            if st.form_submit_button("Aggiorna Password", type="primary", width='stretch'):
                if not old_pass:
                    st.error("Inserisci la password attuale.")
                elif new_pass != confirm_pass:
                    st.error("Le nuove password non coincidono.")
                elif len(new_pass) < 6:
                    st.error("Password troppo corta (min 6 car).")
                else:
                    success, msg = update_user_password_secure(user.email, old_pass, new_pass)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)