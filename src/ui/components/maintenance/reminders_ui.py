import streamlit as st
from datetime import date, timedelta
from src.database import crud
from src.ui.components.maintenance import forms

def render_tab(db, user, last_km):
    """Renderizza l'intero contenuto del tab Promemoria."""
    
    # 1. Area Creazione (Collapsable)
    with st.expander("➕ Crea Nuovo Promemoria", expanded=False):
        _render_creation_form(db, user, last_km)

    st.divider()

    # 2. Griglia Reminders Attivi
    reminders = crud.get_active_reminders(db, user.id)
    
    if not reminders:
        st.info("Nessun promemoria attivo. Inizia a configurare le tue routine!")
        return

    _render_reminders_grid(db, user, reminders, last_km)

def _render_creation_form(db, user, current_km):
    """Form di creazione con logica anti-duplicati e selectbox da Settings."""
    settings = crud.get_settings(db, user.id)
    active_rems = crud.get_active_reminders(db, user.id)
    
    # Filtro: Escludiamo le categorie per cui esiste già un reminder attivo
    existing_titles = [r.title for r in active_rems]
    available_opts = [
        label for label in (settings.reminder_types or []) 
        if label not in existing_titles
    ]

    if not available_opts:
        st.success("Tutte le categorie configurate sono già attive! Vai in Impostazioni per aggiungerne altre.")
        return

    with st.form("new_reminder_form", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        title = c1.selectbox("Categoria", available_opts)
        
        # Trigger: Km o Giorni (Radio button per semplicità UX)
        trigger_type = c2.radio("Scadenza basata su:", ["Chilometri", "Tempo (Giorni)"], horizontal=True)
        
        c3, c4 = st.columns(2)
        freq_km = None
        freq_days = None
        
        if trigger_type == "Chilometri":
            freq_km = c3.number_input("Ogni quanti Km?", min_value=100, step=500, value=10000)
            st.caption(f"Prossimo: {current_km + freq_km} Km")
        else:
            freq_days = c4.number_input("Ogni quanti Giorni?", min_value=1, step=30, value=30)
            
        notes = st.text_area("Note fisse (es. 'Controllare a freddo')", height=68)

        if st.form_submit_button("Salva Promemoria", type="primary", width='stretch'):
            crud.create_reminder(
                db, user.id, title, 
                frequency_km=freq_km, 
                frequency_days=freq_days,
                current_km=current_km,
                current_date=date.today(),
                notes=notes
            )
            st.success("Promemoria attivato!")
            st.rerun()

def _render_reminders_grid(db, user, reminders, current_km):
    """Renderizza le card con Layout Info, Messaggi di Stato e Azioni Dialog."""
    
    cols = st.columns(2)
    
    for idx, rem in enumerate(reminders):
        col = cols[idx % 2]
        with col:
            with st.container(border=True):
                # --- 1. HEADER: Titolo e Menu ---
                c_head, c_menu = st.columns([0.85, 0.15])
                c_head.markdown(f"**{rem.title}**")
                
                with c_menu.popover("⚙️", width='stretch'):
                    if st.button("✏️ Modifica", key=f"edit_btn_{rem.id}", width='stretch'):
                        _render_edit_dialog(db, user, rem)
                    
                    if st.button("✖️ Elimina", key=f"del_btn_{rem.id}", type="primary", width='stretch'):
                        _render_delete_confirm_dialog(db, user, rem)

                # --- 2. INFO DATE/KM (Inserimento e Scadenza) ---
                # Calcolo valori target
                start_label = "-"
                end_label = "-"
                status_msg = ""
                is_expired = False
                progress = 0.0

                if rem.frequency_km:
                    # Logica KM
                    last = rem.last_km_check
                    target = last + rem.frequency_km
                    diff = current_km - last
                    overrun = current_km - target
                    
                    start_label = f"{last} Km"
                    end_label = f"{target} Km"
                    
                    # Calcolo Progresso
                    if diff >= rem.frequency_km:
                        progress = 1.0
                        is_expired = True
                        status_msg = f"⚠️ Attenzione: limite superato da **{overrun} Km**"
                    else:
                        progress = max(0.0, diff / rem.frequency_km)
                        remaining = target - current_km
                        status_msg = f"Mancano **{remaining} Km** alla scadenza"

                elif rem.frequency_days:
                    # Logica GIORNI
                    last = rem.last_date_check
                    target = last + timedelta(days=rem.frequency_days)
                    today = date.today()
                    diff_days = (today - last).days
                    overrun_days = (today - target).days
                    
                    start_label = last.strftime('%d/%m/%y')
                    end_label = target.strftime('%d/%m/%y')
                    
                    if diff_days >= rem.frequency_days:
                        progress = 1.0
                        is_expired = True
                        status_msg = f"⚠️ Attenzione: scaduto da **{overrun_days} giorni**"
                    else:
                        progress = max(0.0, diff_days / rem.frequency_days)
                        remaining = rem.frequency_days - diff_days
                        status_msg = f"Mancano **{remaining} giorni** alla scadenza"

                # Render Info Row
                c_start, c_end = st.columns(2)
                c_start.caption(f"🏁 Inserito:\n**{start_label}**")
                c_end.caption(f"🎯 Target:\n**{end_label}**")
                
                # --- 3. PROGRESS BAR & STATO ---
                # Barra neutra (senza testo interno dinamico come richiesto)
                st.progress(progress)
                
                # Messaggio di stato testuale (Rosso se scaduto, default altrimenti)
                if is_expired:
                    st.markdown(f"<small style='color:red'>{status_msg}</small>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<small>{status_msg}</small>", unsafe_allow_html=True)

                if rem.notes:
                    st.caption(f"📝 {rem.notes}")
                
                st.write("")
                
                # --- 4. AZIONE PRINCIPALE ---
                # Pulsante sempre uguale (Secondary per non essere aggressivo, o Primary se preferisci)
                if st.button("Fatto", key=f"check_rem_{rem.id}", width='stretch', type="secondary"):
                    _render_check_dialog(db, user, rem, current_km)

# --- DIALOGHI ---

@st.dialog("❌ Conferma Eliminazione")
def _render_delete_confirm_dialog(db, user, rem):
    st.warning(f"Sei sicuro di voler eliminare il promemoria **{rem.title}**?")
    st.caption("Questa azione è irreversibile e rimuoverà il promemoria dalla lista attiva.")
    
    c1, c2 = st.columns(2)
    if c1.button("Sì, Elimina", type="primary", width='stretch'):
        crud.delete_reminder(db, user.id, rem.id)
        st.success("Eliminato.")
        st.rerun()
        
    if c2.button("Annulla", width='stretch'):
        st.rerun()

@st.dialog("✏️ Modifica Promemoria")
def _render_edit_dialog(db, user, rem):
    st.write(f"Modifica dettagli per: **{rem.title}**")
    
    # Recupero opzioni per la selectbox (per coerenza, anche se il titolo di solito non si cambia radicalmente)
    settings = crud.get_settings(db, user.id)
    opts = settings.reminder_types or []
    # Assicuriamoci che il titolo attuale sia nella lista per evitare errori
    if rem.title not in opts:
        opts.append(rem.title)
        
    with st.form("edit_rem_form"):
        st.text_input("Categoria", value=rem.title, disabled=True)
        
        c1, c2 = st.columns(2)
        # Logica mista: mostriamo entrambi i campi, uno dei due sarà valorizzato
        new_freq_km = c1.number_input("Frequenza Km", value=rem.frequency_km or 0, step=500)
        new_freq_days = c2.number_input("Frequenza Giorni", value=rem.frequency_days or 0, step=30)
        
        new_notes = st.text_area("Note", value=rem.notes or "")
        
        st.caption("ℹ️ Imposta a 0 la frequenza che non vuoi utilizzare.")
        
        if st.form_submit_button("Salva Modifiche", type="primary", width='stretch'):
            # Validazione: Almeno uno dei due deve essere > 0
            km_val = new_freq_km if new_freq_km > 0 else None
            days_val = new_freq_days if new_freq_days > 0 else None
            
            if not km_val and not days_val:
                st.error("Devi impostare almeno una frequenza (Km o Giorni).")
            else:
                crud.update_reminder(
                    db, user.id, rem.id, 
                    title=rem.title, 
                    freq_km=km_val, 
                    freq_days=days_val, 
                    notes=new_notes
                )
                st.success("Modificato!")
                st.rerun()

# _render_check_dialog rimane invariato come nel codice precedente
@st.dialog("✅ Registra Controllo")
def _render_check_dialog(db, user, reminder, current_km):
    """Dialogo per confermare l'esecuzione della routine."""
    st.write(f"Confermi di aver eseguito: **{reminder.title}**?")
    
    with st.form("check_rem_form"):
        d_date = st.date_input("Data Esecuzione", value=date.today())
        d_km = st.number_input("Km Attuali", value=current_km, step=100)
        d_note = st.text_input("Note opzionali")
        
        if st.form_submit_button("Conferma e Aggiorna", type="primary", width='stretch'):
            crud.log_reminder_execution(
                db, user.id, reminder.id, 
                check_date=d_date, 
                check_km=d_km, 
                notes=d_note
            )
            st.success("Ottimo lavoro! Routine aggiornata.")
            st.rerun()