import streamlit as st
from datetime import date
from src.database import crud
from src.ui.components.maintenance import forms

def perform_save(db, user_id, data, clear_form=True):
    """Helper per il salvataggio fisico (Centralizzato)."""
    crud.create_maintenance(
        db, user_id,
        data['date'],
        data['km'],
        data['type'],
        data['cost'],
        data['desc'],
        expiry_km=data['expiry_km'],
        expiry_date=data['expiry_date']
    )
    st.success("✅ Salvato!")
    if clear_form:
        st.session_state.show_add_form = False
    st.cache_data.clear()
    st.rerun()

@st.dialog("✅ Registra Esecuzione")
def render_resolve_dialog(db, user, origin_record):
    """SCENARIO A: Chiude la vecchia scadenza e ne crea una nuova."""
    st.write(f"Stai registrando l'esecuzione di: **{origin_record.expense_type}**")
    st.caption("Inserisci i dati dell'intervento effettuato oggi. La vecchia scadenza verrà archiviata.")
    
    last_km = crud.get_max_km(db, user.id)
    
    with st.form("resolve_maint_form"):
        # TIPO (Disabilitato)
        st.text_input("Tipo Intervento", value=origin_record.expense_type, disabled=True)
        
        # KM e DATA
        c1, c2 = st.columns(2)
        m_km = c1.number_input("Chilometri Totali", min_value=0, value=last_km, step=100)
        m_date = c2.date_input("Data Intervento", value=date.today())
        
        # COSTO e NOTE
        c3, c4 = st.columns(2)
        m_cost = c3.number_input("Costo (€)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
        m_desc = c4.text_input("Note", value="Rinnovo da scadenza precedente")
        
        st.write("---")
        st.caption("Vuoi impostare già la PROSSIMA scadenza?")
        
        # NUOVE SCADENZE
        c5, c6 = st.columns(2)
        new_exp_km = c5.number_input("Scadenza Km", min_value=0, value=0, step=1000, help="Lascia 0 se non vuoi impostarla")
        new_exp_date = c6.date_input("Scadenza Data", value=None)
        
        if st.form_submit_button("💾 Salva e Chiudi Scadenza", type="primary", width='stretch'):
            # VALIDAZIONI
            if m_cost < 0:
                st.error("Costo non valido.")
                return
            if new_exp_km > 0 and new_exp_km <= m_km:
                st.error(f"⚠️ Errore Scadenza: La nuova scadenza ({new_exp_km} km) deve essere maggiore dei km attuali ({m_km} km).")
                return
            if new_exp_date and new_exp_date <= m_date:
                st.error("⚠️ Errore Scadenza: La data futura deve essere successiva a quella dell'intervento.")
                return

            # ESECUZIONE
            # A. Archiviazione Vecchia
            crud.update_maintenance(db, user.id, origin_record.id, {"expiry_km": None, "expiry_date": None})
            
            # B. Creazione Nuova
            final_exp_km = new_exp_km if new_exp_km > 0 else None
            
            crud.create_maintenance(
                db, user.id,
                m_date,
                m_km,
                origin_record.expense_type,
                m_cost,
                m_desc,
                expiry_km=final_exp_km,
                expiry_date=new_exp_date
            )
            
            st.success("Operazione completata!")
            st.cache_data.clear()
            st.rerun()

@st.dialog("🗑️ Rimuovi Scadenza")
def render_remove_deadline_dialog(db, user, origin_record):
    """SCENARIO B: Rimuove solo la scadenza futura."""
    st.warning(f"Vuoi rimuovere il promemoria per **{origin_record.expense_type}**?")
    st.info("Il record originale della spesa rimarrà nello storico, verrà cancellata solo la data/km di scadenza futura.")
    
    col1, col2 = st.columns(2)
    if col1.button("Sì, Rimuovi", type="primary", width='stretch'):
        crud.update_maintenance(db, user.id, origin_record.id, {"expiry_km": None, "expiry_date": None})
        st.success("Scadenza rimossa.")
        st.cache_data.clear()
        st.rerun()
        
    if col2.button("Annulla", width='stretch'):
        st.rerun()

@st.dialog("⚠️ Conflitto Scadenza")
def render_conflict_dialog(db, user, new_data, old_record):
    """Gestione conflitto in inserimento."""
    st.warning(f"Esiste già una scadenza attiva per **{new_data['type']}**.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Scadenza Esistente")
        if old_record.expiry_km: st.markdown(f"**{old_record.expiry_km} Km**")
        if old_record.expiry_date: st.markdown(f"**{old_record.expiry_date.strftime('%d/%m/%Y')}**")

    with col2:
        st.caption("Nuova Scadenza")
        if new_data['expiry_km']: st.markdown(f"**{new_data['expiry_km']} Km**")
        if new_data['expiry_date']: st.markdown(f"**{new_data['expiry_date'].strftime('%d/%m/%Y')}**")
            
    st.write("---")
    st.write("**Come vuoi procedere?**")

    c_yes, c_no = st.columns(2)
    with c_yes:
        if st.button("Sì, Sovrascrivi", type="primary", width='stretch'):
            crud.update_maintenance(db, user.id, old_record.id, {"expiry_km": None, "expiry_date": None})
            perform_save(db, user.id, new_data)

    with c_no:
        if st.button("No, tieni vecchia", type="secondary", width='stretch'):
            data_no_exp = new_data.copy()
            data_no_exp['expiry_km'] = None; data_no_exp['expiry_date'] = None
            perform_save(db, user.id, data_no_exp)