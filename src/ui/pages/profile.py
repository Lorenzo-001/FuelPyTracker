import streamlit as st
from src.services.auth import update_user_password_secure, update_user_email # <--- Nuovo import

def render():
    st.header("👤 Profilo Utente")
    
    user = st.session_state["user"]
    
    # --- Gestione Date (Ultimo Accesso e Iscrizione) ---
    last_access_str = "N/A"
    created_at_str = "N/A"
    
    # Parsing sicuro date (gestisce sia stringhe ISO che oggetti datetime)
    try:
        # Ultimo accesso
        if user.last_sign_in_at:
            dt_last = user.last_sign_in_at if hasattr(user.last_sign_in_at, 'strftime') else None
            # Se non è oggetto datetime, proviamo a parlarlo o slice stringa (semplificato slice per ora)
            last_access_str = user.last_sign_in_at.strftime('%d/%m/%Y %H:%M') if dt_last else str(user.last_sign_in_at)[:10]

        # Data iscrizione
        if user.created_at:
            dt_created = user.created_at if hasattr(user.created_at, 'strftime') else None
            created_at_str = user.created_at.strftime('%d/%m/%Y') if dt_created else str(user.created_at)[:10]
            
    except Exception:
        # Fallback generico in caso di formati strani
        pass

    # --- SEZIONE 1: Dati Anagrafici ---
    if st.checkbox("📋 Dati Anagrafici", value=True):
        with st.container(border=True):
            col_img, col_data = st.columns([1, 3])
            
            with col_img:
                st.markdown(
                    """
                    <div style="display: flex; justify-content: center; align-items: center; 
                                background-color: #f0f2f6; border-radius: 50%; width: 100px; height: 100px; margin: auto;">
                        <span style="font-size: 50px;">👤</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            with col_data:
                st.subheader(f"{user.email}")
                st.text(f"🆔 - ID Utente: {user.id}")
                st.text(f"📅 - Iscritto dal: {created_at_str}")
                st.text(f"🕒 - Ultimo accesso: {last_access_str}")

    st.write("")
    
    # --- SEZIONE 2: Cambio Email (NUOVA) ---
    if st.checkbox("📧 Modifica Email", value=False):
        with st.container(border=True):
            st.info("⚠️ Attenzione: Modificando l'email, dovrai confermare il nuovo indirizzo tramite il link che ti verrà inviato.")
            
            with st.form("change_email_form"):
                new_email = st.text_input("Nuovo Indirizzo Email")
                
                if st.form_submit_button("Invia Conferma Cambio Email", type="secondary", use_container_width=True):
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
                
                if st.form_submit_button("Aggiorna Password", type="primary", use_container_width=True):
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