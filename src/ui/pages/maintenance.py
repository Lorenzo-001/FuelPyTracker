import streamlit as st
import pandas as pd
from datetime import date
from database.core import get_db
from database import crud
from ui.components import grids, kpi  # Importiamo il componente grafico
import textwrap

def render():
    st.header("🔧 Registro Manutenzioni")
    
    # --- INIT STATE ---
    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False
    if "active_operation" not in st.session_state:
        st.session_state.active_operation = None
    if "selected_record_id" not in st.session_state:
        st.session_state.selected_record_id = None

    db = next(get_db())
    records = crud.get_all_maintenances(db)
    
    # --- DATA PREP ---
    current_year = date.today().year
    db_years = sorted(list(set(r.date.year for r in records)), reverse=True)
    if not db_years: db_years = [current_year]
    
    year_options = ["Tutti gli anni"] + db_years
    try:
        default_idx = db_years.index(current_year) + 1
    except ValueError:
        default_idx = 0 

    # ---------------------------------------------------------
    # 1. TOP CONTROL STRIP (Anno | KPI Card | Bottone)
    # ---------------------------------------------------------
    # Layout responsivo: Su mobile questi 3 elementi andranno uno sotto l'altro automaticamente
    c_year, c_kpi, c_btn = st.columns([1.5, 1.5, 1.2], gap="small", vertical_alignment="bottom")

    # A. Selectbox Anno
    with c_year:
        selected_year_option = st.selectbox(
            "📅 Anno Riferimento", 
            year_options, 
            index=default_idx,
            key="unified_year_filter",
            label_visibility="visible" # Meglio visibile su mobile
        )

    # Filtro Dati
    if selected_year_option == "Tutti gli anni":
        records_filtered = records 
        label_kpi = "Storico"
    else:
        records_filtered = [r for r in records if r.date.year == selected_year_option]
        label_kpi = str(selected_year_option)

    # Calcolo Totale
    total_spent = sum(r.cost for r in records_filtered)

    # B. KPI Card (Custom HTML)
    with c_kpi:
        # Usiamo un container per allineare l'HTML verticalmente alla selectbox
        # il padding top simula l'allineamento con la label della selectbox
        kpi.render_maintenance_card(total_spent, label_kpi)

    # C. Bottone Nuovo Intervento
    with c_btn:
            btn_label = "Chiudi" if st.session_state.show_add_form else "➕ Nuovo"
            btn_type = "secondary" if st.session_state.show_add_form else "primary"
            
            # Il bottone è alto ~42px. Essendo allineato in basso (bottom),
            # sarà perfettamente in linea con il campo input della selectbox e la parte inferiore della card.
            if st.button(btn_label, type=btn_type, use_container_width=True):
                st.session_state.show_add_form = not st.session_state.show_add_form
                st.rerun()

    # ---------------------------------------------------------
    # 2. FORM DI INSERIMENTO (Expander controllato)
    # ---------------------------------------------------------
    if st.session_state.show_add_form:
        with st.container(border=True):
            st.markdown("##### ✨ Nuovo Intervento")
            with st.form("new_maint_form", clear_on_submit=True):
                last_km = crud.get_max_km(db)
                # Uso Helper per generare i campi
                form_data = _render_maint_form(date.today(), last_km, "Tagliando", 0.0, "")
                
                if st.form_submit_button("Salva Intervento", type="primary", use_container_width=True):
                    if form_data['cost'] > 0:
                        crud.create_maintenance(db, form_data['date'], form_data['km'], form_data['type'], form_data['cost'], form_data['desc'])
                        st.success("✅ Salvato!")
                        st.session_state.show_add_form = False
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Inserire un costo valido.")

    st.write("") # Spacer

    # ---------------------------------------------------------
    # 3. TABS: STORICO E GESTIONE
    # ---------------------------------------------------------
    tab_history, tab_manage = st.tabs(["📋 Storico", "🛠️ Gestione"])

    # --- TAB 1: STORICO (Tabella) ---
    with tab_history:
        # Filtri Categoria
        all_categories = sorted(list(set(r.expense_type for r in records)))
        selected_cats = st.multiselect(
            "Filtra Categoria", 
            all_categories, 
            placeholder="Tutte le categorie...",
            label_visibility="collapsed"
        )

        final_records = records_filtered
        if selected_cats:
            final_records = [r for r in final_records if r.expense_type in selected_cats]

        if final_records:
            df_display = grids.build_maintenance_dataframe(final_records)
            st.dataframe(
                df_display.drop(columns=["_obj"]), 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": None,
                    "Descrizione": st.column_config.TextColumn(width="medium"),
                    "Tipo": st.column_config.TextColumn(width="small")
                }
            )
        else:
            st.info("Nessun dato da visualizzare.")

    # --- TAB 2: GESTIONE (Edit/Delete) ---
    with tab_manage:
        if records:
            # Selezione Anno Gestione
            mgmt_years = sorted(list(set(r.date.year for r in records)), reverse=True)
            sel_mgmt_year = st.selectbox("Anno Gestione", mgmt_years, index=0, key="mgmt_year_maint")
            
            recs_mgmt = [r for r in records if r.date.year == sel_mgmt_year]
            
            if recs_mgmt:
                # Selezione Record
                opts = {f"{r.date.strftime('%d/%m')} - {r.expense_type} (€ {r.cost:.0f})": r.id for r in recs_mgmt}
                sel_label = st.selectbox("Seleziona Intervento", list(opts.keys()))
                target_id = opts[sel_label] if sel_label else None
                
                # Bottoni Azione
                c_edit, c_del = st.columns(2)
                if c_edit.button("✏️ Modifica", use_container_width=True):
                    st.session_state.active_operation = "edit"
                    st.session_state.selected_record_id = target_id
                    st.rerun()
                if c_del.button("🗑️ Elimina", type="primary", use_container_width=True):
                    st.session_state.active_operation = "delete"
                    st.session_state.selected_record_id = target_id
                    st.rerun()

                # Logica Pannelli Dinamici
                if st.session_state.active_operation and st.session_state.selected_record_id == target_id:
                    target_rec = next((r for r in records if r.id == target_id), None)
                    if target_rec:
                        st.divider()
                        
                        # EDIT FORM
                        if st.session_state.active_operation == "edit":
                            st.markdown(f"**Modifica:** {target_rec.date.strftime('%d/%m/%Y')}")
                            with st.form("edit_maint_form"):
                                # Uso Helper precompilato
                                d_edit = _render_maint_form(target_rec.date, target_rec.total_km, target_rec.expense_type, target_rec.cost, target_rec.description)
                                
                                if st.form_submit_button("Aggiorna", type="primary", use_container_width=True):
                                    changes = {"date": d_edit['date'], "total_km": d_edit['km'], "expense_type": d_edit['type'], "cost": d_edit['cost'], "description": d_edit['desc']}
                                    crud.update_maintenance(db, target_id, changes)
                                    st.success("Aggiornato!")
                                    st.session_state.active_operation = None
                                    st.cache_data.clear()
                                    st.rerun()
                            
                            if st.button("Annulla", use_container_width=True):
                                st.session_state.active_operation = None
                                st.rerun()

                        # DELETE CONFIRM
                        elif st.session_state.active_operation == "delete":
                            st.error(f"Eliminare {target_rec.expense_type}?")
                            cd1, cd2 = st.columns(2)
                            if cd1.button("Sì, Elimina", type="primary", use_container_width=True):
                                crud.delete_maintenance(db, target_id)
                                st.success("Eliminato.")
                                st.session_state.active_operation = None
                                st.cache_data.clear()
                                st.rerun()
                            if cd2.button("No", use_container_width=True):
                                st.session_state.active_operation = None
                                st.rerun()
            else:
                st.warning("Nessun intervento in questo anno.")
        else:
            st.info("Nessun dato nel database.")

    db.close()

# --- HELPER INTERNO ---
def _render_maint_form(d_date, d_km, d_type, d_cost, d_desc):
    """Genera i campi del form manutenzione standardizzato."""
    c1, c2 = st.columns(2)
    
    date_val = c1.date_input("Data", value=d_date)
    km_val = c1.number_input("Odometro", value=d_km, step=1)
    
    cat_opts = ["Tagliando", "Gomme", "Batteria", "Revisione", "Bollo", "Riparazione", "Altro"]
    # Gestione indice per selectbox
    try:
        idx_type = cat_opts.index(d_type)
    except ValueError:
        idx_type = 6 # Altro
        
    type_val = c2.selectbox("Categoria", cat_opts, index=idx_type)
    cost_val = c2.number_input("Costo €", value=float(d_cost), min_value=0.0, step=1.0, format="%.2f")
    
    desc_val = st.text_area("Note / Dettagli", value=d_desc, height=80)
    
    return {
        "date": date_val, "km": km_val, "type": type_val, 
        "cost": cost_val, "desc": desc_val
    }