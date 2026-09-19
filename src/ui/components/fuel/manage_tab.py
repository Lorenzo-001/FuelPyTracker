"""Fuel management tab: select / edit / delete refuelings."""
import streamlit as st
from src.database import crud
from src.ui.components.fuel import forms
from src.demo import writes_disabled


def render_management_tab(db, user, all_records, years, def_idx, settings):
    if not all_records:
        st.info("Nessun dato modificabile.")
        return

    # Selezione Record
    mgmt_year = st.selectbox("Anno Gestione", years, index=def_idx, key="mgmt_year_sel")
    recs_year = [r for r in all_records if r.date.year == mgmt_year]
    
    if not recs_year:
        st.warning("Nessun record in questo anno.")
        return

    opts = {f"{r.date.strftime('%d/%m')} - {r.total_km}km (€ {r.total_cost:.2f})": r.id for r in recs_year}
    sel_label = st.selectbox("Seleziona Record", list(opts.keys()))
    target_id = opts[sel_label] if sel_label else None
    
    # Pulsanti Azione
    c1, c2 = st.columns(2)
    if c1.button("✏️ Modifica", width="stretch", disabled=writes_disabled()):
        st.session_state.active_operation = "edit"
        st.session_state.selected_record_id = target_id
        st.rerun()
    if c2.button("❌ Elimina", type="primary", width="stretch", disabled=writes_disabled()):
        st.session_state.active_operation = "delete"
        st.session_state.selected_record_id = target_id
        st.rerun()
    
    # Gestione Pannelli Operativi
    if st.session_state.active_operation and st.session_state.selected_record_id == target_id:
        target_rec = next((r for r in all_records if r.id == target_id), None)
        if target_rec:
            st.divider()
            if st.session_state.active_operation == "edit":
                _handle_edit_flow(db, user.id, target_rec, settings) # Passa user.id
            elif st.session_state.active_operation == "delete":
                _handle_delete_flow(db, user.id, target_id)


def _handle_edit_flow(db, user_id, rec, settings):
    st.markdown(f"**Modifica Record:** {rec.date}")
    
    with st.form("fuel_form_edit"):
        # Calcolo range dinamico per lo slider del prezzo
        min_pe, max_pe = max(0.0, rec.price_per_liter-0.5), rec.price_per_liter+0.5
        
        # Se il record esistente ha un costo superiore al limite impostato nei settings,
        # il max_value del form deve essere il maggiore tra il limite configurato e il valore attuale.
        safe_max_cost = max(float(settings.max_total_cost), float(rec.total_cost))
        
        # Riutilizzo componente UI form
        edit_data = forms.render_refueling_inputs(
            rec.date, rec.total_km, rec.price_per_liter, rec.total_cost, 
            rec.is_full_tank, rec.notes, 
            min_pe, max_pe, 
            safe_max_cost,
            last_km_known=rec.total_km,
            key_suffix="edit"
        )
        
        if st.form_submit_button("Aggiorna", type="primary", width="stretch", disabled=writes_disabled()):
            # Nota: In edit non controlliamo "last_km" stretto come in insert per flessibilità
            new_liters = edit_data['cost'] / edit_data['price'] if edit_data['price'] > 0 else 0
            
            changes = {
                "date": edit_data['date'], "total_km": edit_data['km'], 
                "price_per_liter": edit_data['price'], "total_cost": edit_data['cost'], 
                "liters": new_liters, "is_full_tank": edit_data['full'], "notes": edit_data['notes']
            }
            
            crud.update_refueling(db, user_id, rec.id, changes)
            st.success("Record aggiornato!")
            st.session_state.active_operation = None
            if "price_slider_edit" in st.session_state:
                del st.session_state["price_slider_edit"]
            if "last_default_price_edit" in st.session_state:
                del st.session_state["last_default_price_edit"]
            st.rerun()
            
    if st.button("Annulla", width="stretch"):
        st.session_state.active_operation = None
        if "price_slider_edit" in st.session_state:
            del st.session_state["price_slider_edit"]
        if "last_default_price_edit" in st.session_state:
            del st.session_state["last_default_price_edit"]
        st.rerun()


def _handle_delete_flow(db, user_id, record_id):
    st.error("Sei sicuro di voler eliminare definitivamente questo record?")
    cd1, cd2 = st.columns(2)
    if cd1.button("Sì, Elimina", type="primary", width="stretch", disabled=writes_disabled()):
        crud.delete_refueling(db, user_id, record_id)
        st.success("Eliminato."); st.session_state.active_operation = None; st.rerun()
    if cd2.button("No, Annulla", width="stretch"):
        st.session_state.active_operation = None; st.rerun()
