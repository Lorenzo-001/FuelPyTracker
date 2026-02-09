import streamlit as st
from src.services.business import maintenance_logic
from src.ui.components.maintenance import grids, forms
from src.database import crud
from datetime import date

def render_history_tab(records_filtered, all_records):
    """Renderizza il tab Storico (Dataframe)."""
    all_cats = maintenance_logic.get_all_categories(all_records)
    sel_cats = st.multiselect("Filtra Categoria", all_cats, placeholder="Tutte...", label_visibility="collapsed")
    
    final_recs = maintenance_logic.filter_records_by_category(records_filtered, sel_cats)

    if final_recs:
        df = grids.build_maintenance_dataframe(final_recs)
        st.dataframe(
            df.drop(columns=["_obj"]), 
            width="stretch", hide_index=True,
            column_config={
                "ID": None,
                "Descrizione": st.column_config.TextColumn(width="medium"),
                "Tipo": st.column_config.TextColumn(width="small")
            }
        )
    else:
        st.info("Nessun dato da visualizzare.")

def render_management_tab(db, user, all_records):
    """Renderizza il tab Gestione (Modifica/Elimina)."""
    if not all_records:
        st.info("Nessun dato nel database."); return

    # Filtro Anno
    mgmt_years = maintenance_logic.get_available_years(all_records)
    sel_year = st.selectbox("Anno Gestione", mgmt_years, index=0, key="mgmt_year_maint")
    recs_mgmt, _ = maintenance_logic.filter_records_by_year(all_records, sel_year)
    
    if not recs_mgmt:
        st.warning("Nessun intervento in questo anno."); return

    # Selezione
    opts = {f"{r.date.strftime('%d/%m')} - {r.expense_type} (€ {r.cost:.0f})": r.id for r in recs_mgmt}
    sel_label = st.selectbox("Seleziona Intervento", list(opts.keys()))
    target_id = opts[sel_label] if sel_label else None
    
    # Pulsanti Azione
    c1, c2 = st.columns(2)
    if c1.button("✏️ Modifica", width="stretch"):
        st.session_state.active_operation = "edit"
        st.session_state.selected_record_id = target_id
        st.rerun()
    if c2.button("🗑️ Elimina", type="primary", width="stretch"):
        st.session_state.active_operation = "delete"
        st.session_state.selected_record_id = target_id
        st.rerun()

    # Logica Pannelli
    if st.session_state.active_operation and st.session_state.selected_record_id == target_id:
        target_rec = next((r for r in all_records if r.id == target_id), None)
        if target_rec:
            st.divider()
            if st.session_state.active_operation == "edit":
                _handle_edit(db, user.id, target_rec)
            elif st.session_state.active_operation == "delete":
                _handle_delete(db, user.id, target_id, target_rec.expense_type)

def _handle_edit(db, user_id, rec):
    st.markdown(f"**Modifica:** {rec.date.strftime('%d/%m/%Y')}")
    with st.form("edit_maint_form"):
        d_edit = forms.render_maintenance_inputs(
            rec.date, rec.total_km, rec.expense_type, rec.cost, rec.description,
            default_expiry_km=rec.expiry_km, default_expiry_date=rec.expiry_date
        )
        
        if st.form_submit_button("Aggiorna", type="primary", width="stretch"):
            # Validazioni
            if d_edit['cost'] < 0:
                st.error("Inserire un costo valido.")
            elif d_edit['expiry_km'] and d_edit['expiry_km'] <= d_edit['km']:
                st.error(f"⚠️ Errore Logico: La scadenza ({d_edit['expiry_km']} km) deve essere maggiore dei km attuali.")
            elif d_edit['expiry_date'] and d_edit['expiry_date'] <= d_edit['date']:
                st.error("⚠️ Errore Logico: La data di scadenza deve essere successiva alla data dell'intervento.")
            else:
                changes = {
                    "date": d_edit['date'], "total_km": d_edit['km'], 
                    "expense_type": d_edit['type'], "cost": d_edit['cost'], 
                    "description": d_edit['desc'], "expiry_km": d_edit['expiry_km'],
                    "expiry_date": d_edit['expiry_date']
                }
                crud.update_maintenance(db, user_id, rec.id, changes)
                st.success("Aggiornato!")
                st.session_state.active_operation = None
                st.cache_data.clear()
                st.rerun()
            
    if st.button("Annulla", width="stretch"):
        st.session_state.active_operation = None; st.rerun()

def _handle_delete(db, user_id, rec_id, rec_type):
    st.error(f"Eliminare {rec_type}?")
    c1, c2 = st.columns(2)
    if c1.button("Sì, Elimina", type="primary", width="stretch"):
        crud.delete_maintenance(db, user_id, rec_id)
        st.success("Eliminato.")
        st.session_state.active_operation = None
        st.cache_data.clear()
        st.rerun()
    if c2.button("No", width="stretch"):
        st.session_state.active_operation = None; st.rerun()


def _render_reminder_tab(db, user, settings, active_reminders, current_km):
    """Gestisce la creazione e visualizzazione card dei reminder attivi."""
    
    # 1. Form di Creazione Rapida (Anti-Duplicati)
    with st.expander("➕ Crea Nuovo Promemoria", expanded=False):
        with st.form("new_reminder_form", border=False):
            # Logica Anti-Duplicati: Filtriamo le categorie già presenti nei reminder attivi
            active_cats = [r.category for r in active_reminders]
            available_cats = [c for c in (settings.reminder_types or []) if c not in active_cats]
            
            if available_cats:
                c1, c2, c3 = st.columns(3)
                cat = c1.selectbox("Categoria", available_cats)
                target_km = c2.number_input("Scadenza Km (Intervallo)", min_value=1000, value=15000, step=1000)
                # target_date = c3.date_input("Scadenza Temporale", value=date.today() + timedelta(days=365))
                target_months = c3.number_input("Scadenza Mesi", min_value=1, value=12)

                if st.form_submit_button("Salva Promemoria", type="primary", use_container_width=True):
                    # Ipotetica chiamata al CRUD
                    crud.create_reminder(db, user.id, cat, target_km, target_months, start_km=current_km)
                    st.success(f"Promemoria per {cat} attivato!")
                    st.rerun()
            else:
                st.info("Tutte le categorie configurate hanno già un promemoria attivo.")

    st.divider()

    # 2. Grid Visualizzazione Card
    if not active_reminders:
        st.info("Nessun promemoria attivo. Creane uno sopra.")
        return

    # Layout a griglia responsive
    cols = st.columns(2) # 2 card per riga su desktop
    for idx, reminder in enumerate(active_reminders):
        with cols[idx % 2]:
            _render_reminder_card(db, user, reminder, current_km)

def _render_reminder_card(db, user, reminder, current_km):
    """Renderizza una singola card con Health Bar e Popover Actions."""
    
    # Calcolo Logica Health Bar (Consumo)
    # Km percorsi dall'ultimo reset
    km_driven = current_km - reminder.last_reset_km
    km_progress = min(km_driven / reminder.interval_km, 1.0)
    
    # Tempo passato (se presente logica temporale)
    # days_passed = (date.today() - reminder.last_reset_date).days
    # time_progress = min(days_passed / (reminder.interval_months * 30), 1.0)
    
    # La salute è determinata dal fattore più critico (es. ho fatto pochi km ma è passato un anno)
    # health_factor = max(km_progress, time_progress) 
    health_factor = km_progress # Semplificazione per esempio
    
    # Colore Barra: Verde (<70%), Giallo (70-90%), Rosso (>90%)
    bar_color = "red" if health_factor > 0.9 else "orange" if health_factor > 0.7 else "green"
    
    with st.container(border=True):
        # Header Card
        c_tit, c_act = st.columns([4, 1], vertical_alignment="center")
        c_tit.markdown(f"**{reminder.category}**")
        
        # Action Menu (Popover)
        with c_act.popover("⋮", use_container_width=True):
            st.markdown(f"**Gestione {reminder.category}**")
            
            # Action 1: Modifica (Placeholder)
            if st.button("✏️ Modifica Parametri", key=f"edit_{reminder.id}", use_container_width=True):
                st.toast("Funzionalità modifica in arrivo")
            
            # Action 2: Archiviazione (DONE)
            with st.expander("✅ Segna come Fatto"):
                with st.form(f"done_form_{reminder.id}"):
                    cost = st.number_input("Costo Intervento (€)", min_value=0.0, step=10.0)
                    note = st.text_input("Note", value="Tagliando periodico")
                    
                    if st.form_submit_button("Conferma e Archivia"):
                        # 1. Crea record nello storico
                        crud.create_maintenance(db, user.id, reminder.category, cost, date.today(), note, km=current_km)
                        # 2. Resetta il reminder (nuovo start_km = current_km)
                        crud.reset_reminder(db, reminder.id, current_km)
                        st.toast("Intervento registrato e scadenze aggiornate!")
                        st.rerun()

            # Action 3: Elimina
            if st.button("🗑️ Elimina Reminder", key=f"del_{reminder.id}", type="primary", use_container_width=True):
                crud.delete_reminder(db, reminder.id)
                st.rerun()

        # Body Card (Health Bar)
        remaining_km = reminder.interval_km - km_driven
        st.progress(health_factor)
        
        # Dettagli testuali
        c_det1, c_det2 = st.columns(2)
        c_det1.caption(f"Percorsi: **{km_driven} km**")
        
        if remaining_km > 0:
            c_det2.caption(f"Mancano: **{remaining_km} km**")
        else:
            c_det2.markdown(f":red[Scaduto da **{abs(remaining_km)} km**]")