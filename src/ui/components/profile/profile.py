import streamlit as st
import time
from src.services.auth.auth_service import update_user_password_secure, update_user_email
from src.services.data.storage import upload_avatar, get_avatar_url

#TODO: Fix componenti UI refactoring

@st.fragment
def render():
    st.header("👤 Profilo Utente")

    # Inizializza il timestamp una volta sola
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

    # --- SEZIONE 1: Dati Anagrafici + Foto ---
    if st.checkbox("📋 Dati Anagrafici", value=True):
        with st.container(border=True):
            
            # Recupero URL Avatar
            avatar_url = get_avatar_url(user.id)

            if avatar_url:
                # Usa la versione memorizzata nello stato, così rimane fissa
                # finché non carichi una nuova foto
                avatar_url = f"{avatar_url}?v={st.session_state['avatar_version']}"

            # Layout a due colonne: Avatar (SX) - Dati (DX)
            col_img, col_data = st.columns([1, 4], vertical_alignment="center", gap="large")  

            with col_img:
                # CSS dinamico per background
                bg_image_style = f"background-image: url('{avatar_url}'); background-size: cover; background-position: center;" if avatar_url else ""
                icon_html = "" if avatar_url else '<span style="font-size: 60px;">👤</span>'
                
                # Avatar Quadrato Geometrico (SOLO VISUALIZZAZIONE)
                st.markdown(
                    f"""
                    <div style="
                        display: flex; 
                        justify-content: center; 
                        align-items: center; 
                        background-color: #e0e0e0; 
                        border-radius: 12px;
                        width: 140px; 
                        height: 140px; 
                        border: 2px solid #ccc;
                        {bg_image_style}
                    ">
                        {icon_html}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

            with col_data:
                # word-wrap: break-word -> Fondamentale per ID e Email lunghi su mobile
                st.markdown(f"""
                <div style="
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    height: 100%;
                    width: 100%;
                    word-wrap: break-word; 
                    overflow-wrap: break-word;
                ">
                    <h3 style="
                        margin: 10px 10px 10px 20px; 
                        padding: 6px 14px; 
                        font-size: 1.2rem; 
                        font-weight: 600;
                        font-style: italic;
                        color: #f1c40f;
                        background: linear-gradient(135deg, #2c2c2c, #1a1a1a);
                        border-radius: 12px;
                        display: inline-block;
                        word-break: break-all; 
                        line-height: 1.2;
                        box-shadow: 0 0 10px rgba(241, 196, 15, 0.4);
                    ">
                        ⭐ {user.email}
                    </h3>
                    <ul style="list-style-type: none; padding: 0; margin: 0; line-height: 1.8;">
                        <li><strong>ID Utente:</strong> <code style="padding: 2px 5px; border-radius: 4px;">{user.id}</code></li>
                        <li><strong>Iscritto dal:</strong> <code style="padding: 2px 5px; border-radius: 4px;">{created_at_str}</code></li>
                        <li><strong>Ultimo accesso:</strong> <code style="padding: 2px 5px; border-radius: 4px;">{last_access_str}</code></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            # --- UPLOAD SPOSTATO QUI SOTTO ---
            st.divider()
            # Usiamo un expander per nascondere il box ingombrante di default
            with st.expander("📷 Modifica Foto Profilo", expanded=False):
                # 1. Inizializziamo una key nel session state se non esiste
                if "uploader_key" not in st.session_state:
                    st.session_state["uploader_key"] = 0

                # 2. Assegniamo la key dinamica al widget
                uploaded_file = st.file_uploader(
                    "Carica una nuova immagine", 
                    type=['png', 'jpg', 'jpeg'],
                    key=f"avatar_uploader_{st.session_state['uploader_key']}"
                )
                
                if uploaded_file is not None:
                    with st.spinner("Caricamento in corso..."):
                        new_url = upload_avatar(user.id, uploaded_file)
                        
                        if new_url:
                            st.success("✅ Avatar aggiornato con successo!")
                            time.sleep(1) 
                            
                            # 3. Incrementiamo la key per "pulire" il widget al prossimo riavvio
                            st.session_state["uploader_key"] += 1

                            # Solo adesso cambiamo l'URL per forzare il browser a scaricare la nuova immagine
                            st.session_state["avatar_version"] = int(time.time())
                            
                            # 4. Ricarichiamo la pagina
                            st.rerun()
                        else:
                            st.error("Errore durante l'upload.")

    st.write("")
    
    # --- SEZIONE 2: Cambio Email ---
    if st.checkbox("📧 Modifica Email", value=False):
        with st.container(border=True):
            st.info("⚠️ Attenzione: Modificando l'email, dovrai confermare il nuovo indirizzo tramite il link che ti verrà inviato.")
            
            with st.form("change_email_form"):
                new_email = st.text_input("Nuovo Indirizzo Email")
                
                if st.form_submit_button("Invia Conferma Cambio Email", type="secondary", width='stretch'):
                    if not new_email or "@" not in new_email:
                        st.error("Inserisci un'email valida.")
                    elif new_email == user.email:
                        st.warning("La nuova email è uguale a quella attuale.")
                    else:
                        success, msg = update_user_email(new_email)
                        if success:
                            st.success(msg)
                        else:
                            st.error(f"Errore: {msg}")

    st.write("")

    # --- SEZIONE 3: Sicurezza Password ---
    if st.checkbox("🔐 Sicurezza (Cambio Password)", value=False):
        with st.container(border=True):
            st.info("Per sicurezza, è necessario inserire la password attuale.")
            
            with st.form("change_pass_form_secure"):
                old_pass = st.text_input("Password Attuale", type="password")
                st.divider()
                new_pass = st.text_input("Nuova Password", type="password")
                confirm_pass = st.text_input("Conferma Nuova Password", type="password")
                
                if st.form_submit_button("Aggiorna Password", type="primary", width='stretch'):
                    if not old_pass:
                        st.error("Inserisci la password attuale.")
                    elif new_pass != confirm_pass:
                        st.error("Le nuove password non coincidono.")
                    elif len(new_pass) < 6:
                        st.error("La nuova password deve essere di almeno 6 caratteri.")
                    else:
                        success, msg = update_user_password_secure(user.email, old_pass, new_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)