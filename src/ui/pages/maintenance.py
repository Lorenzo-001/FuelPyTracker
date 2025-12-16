import streamlit as st
from datetime import date
from src.database.core import get_db
from src.database import crud
from src.ui.components import grids, kpi, forms
from src.services import maintenance_logic

def render():
    """Vista Principale: Registro Manutenzioni (Refactored & Multi-Tenant)."""
    st.header("🔧 Registro Manutenzioni")
    
    # --- 1. Init Stato & DB ---
    _init_session_state()
    user = st.session_state["user"]

    db = next(get_db())
    records = crud.get_all_maintenances(db, user.id)
    
    # --- 2. Top Bar & Filtri Globali ---
    # Logica recupero anni
    db_years = maintenance_logic.get_available_years(records)
    year_options = ["Tutti gli anni"] + db_years
    
    # Calcolo indice default (anno corrente)
    curr_year = date.today().year
    def_idx = db_years.index(curr_year) + 1 if curr_year in db_years else 0
    
    # Render controlli superiori
    c_year, c_kpi, c_btn = st.columns([1.5, 1.5, 1.2], gap="small", vertical_alignment="bottom")
    
    with c_year:
        sel_year_opt = st.selectbox("📅 Anno Riferimento", year_options, index=def_idx, key="maint_year_filter")

    # Applicazione Filtro Logico
    recs_filtered, label_kpi = maintenance_logic.filter_records_by_year(records, sel_year_opt)
    total_spent = sum(r.cost for r in recs_filtered)

    with c_kpi:
        kpi.render_maintenance_card(total_spent, label_kpi)

    with c_btn:
        _render_add_button()

    # --- 3. Area Inserimento (Add Form) ---
    if st.session_state.show_add_form:
        _render_add_form(db, user)

    st.write("") # Spacer

    # --- 4. Tabs: Storico & Gestione ---
    tab_hist, tab_mgmt = st.tabs(["📋 Storico", "🛠️ Gestione"])

    with tab_hist:
        _render_history_tab(recs_filtered, records) # Passiamo records originali per le categorie

    with tab_mgmt:
        _render_management_tab(db, user, records) # Qui serve tutto lo storico per permettere modifiche su altri anni

    db.close()

# ==========================================
# PRIVATE HELPER FUNCTIONS (View Logic)
# ==========================================

def _init_session_state():
    if "show_add_form" not in st.session_state: st.session_state.show_add_form = False
    if "active_operation" not in st.session_state: st.session_state.active_operation = None
    if "selected_record_id" not in st.session_state: st.session_state.selected_record_id = None

def _render_add_button():
    lbl = "Chiudi" if st.session_state.show_add_form else "➕ Nuovo"
    typ = "secondary" if st.session_state.show_add_form else "primary"
    if st.button(lbl, type=typ, width="stretch"):
        st.session_state.show_add_form = not st.session_state.show_add_form
        st.rerun()

def _render_add_form(db, user):
    with st.container(border=True):
        st.markdown("##### ✨ Nuovo Intervento")
        with st.form("new_maint_form", clear_on_submit=True):
            last_km = crud.get_max_km(db, user.id) # user.id
            # Form delegato a ui/forms.py
            data = forms.render_maintenance_inputs(date.today(), last_km, "Tagliando", 0.0, "")
            
            if st.form_submit_button("Salva Intervento", type="primary", width="stretch"):
                if data['cost'] >= 0:
                    crud.create_maintenance(
                        db, user.id,
                        data['date'], data['km'], data['type'], data['cost'], data['desc']
                    )
                    st.success("✅ Salvato!")
                    st.session_state.show_add_form = False
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Inserire un costo valido.")

def _render_history_tab(records_filtered, all_records):
    # Filtro Categoria
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

def _render_management_tab(db, user, all_records):
    if not all_records:
        st.info("Nessun dato nel database."); return

    # Selezione Anno per Gestione (indipendente dal filtro top bar)
    mgmt_years = maintenance_logic.get_available_years(all_records)
    sel_year = st.selectbox("Anno Gestione", mgmt_years, index=0, key="mgmt_year_maint")
    
    recs_mgmt, _ = maintenance_logic.filter_records_by_year(all_records, sel_year)
    
    if not recs_mgmt:
        st.warning("Nessun intervento in questo anno."); return

    # Selezione Record
    opts = {f"{r.date.strftime('%d/%m')} - {r.expense_type} (€ {r.cost:.0f})": r.id for r in recs_mgmt}
    sel_label = st.selectbox("Seleziona Intervento", list(opts.keys()))
    target_id = opts[sel_label] if sel_label else None
    
    # Pulsanti
    c1, c2 = st.columns(2)
    if c1.button("✏️ Modifica", width="stretch"):
        st.session_state.active_operation = "edit"
        st.session_state.selected_record_id = target_id
        st.rerun()
    if c2.button("🗑️ Elimina", type="primary", width="stretch"):
        st.session_state.active_operation = "delete"
        st.session_state.selected_record_id = target_id
        st.rerun()

    # Pannelli Edit/Delete
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
        # Reuse Form UI
        d_edit = forms.render_maintenance_inputs(rec.date, rec.total_km, rec.expense_type, rec.cost, rec.description)
        
        if st.form_submit_button("Aggiorna", type="primary", width="stretch"):
            changes = {
                "date": d_edit['date'], "total_km": d_edit['km'], 
                "expense_type": d_edit['type'], "cost": d_edit['cost'], 
                "description": d_edit['desc']
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