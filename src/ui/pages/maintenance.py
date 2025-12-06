import streamlit as st
import pandas as pd
import streamlit.components.v1 as components 
from datetime import date
from database.core import get_db
from database import crud
from ui.components import grids

def render():
    st.header("🔧 Registro Manutenzioni")
    
    # Spazietto richiesto tra Titolo e Contenuto
    st.write("") 
    st.write("")

    # Inizializzazione Stato Sessione
    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False
    if "active_operation" not in st.session_state:
        st.session_state.active_operation = None
    if "selected_record_id" not in st.session_state:
        st.session_state.selected_record_id = None

    db = next(get_db())
    records = crud.get_all_maintenances(db)
    
    # ---------------------------------------------------------
    # PREPARAZIONE DATI (Anni disponibili + Opzione "Tutti")
    # ---------------------------------------------------------
    current_year = date.today().year
    
    # Set degli anni presenti nel DB
    db_years = sorted(list(set(r.date.year for r in records)), reverse=True)
    if not db_years:
        db_years = [current_year]
    
    # Creiamo la lista opzioni mista: Stringa ("Tutti gli anni") + Interi (Anni)
    year_options = ["Tutti gli anni"] + db_years
    
    # Calcolo indice di default (Anno corrente)
    try:
        default_idx = db_years.index(current_year) + 1
    except ValueError:
        default_idx = 0 

    # ---------------------------------------------------------
    # 1. LAYOUT PRINCIPALE (Colonna SX: KPI/Btn - Colonna DX: Tabella)
    # ---------------------------------------------------------
    
    col_ctrl, col_data = st.columns([1, 3.5], gap="medium")

    # Variabile per contenere i record filtrati per anno
    records_year_filtered = []

    # --- COLONNA SINISTRA: Controlli e KPI ---
    with col_ctrl:
        with st.container(border=True):
            # A. Selectbox Unificata (Controlla tutto)
            selected_year_option = st.selectbox(
                "📅 Anno Spesa", 
                year_options, 
                index=default_idx,
                key="unified_year_filter"
            )
            
            # B. Logica Filtro Anno
            if selected_year_option == "Tutti gli anni":
                records_year_filtered = records 
                label_kpi = "Totale Storico"
            else:
                records_year_filtered = [r for r in records if r.date.year == selected_year_option]
                label_kpi = f"Spesa {selected_year_option}"

            # C. Calcolo KPI
            total_spent_kpi = sum(r.cost for r in records_year_filtered)
            
            # D. Visualizzazione KPI
            st.metric(
                label=label_kpi, 
                value=f"{total_spent_kpi:.2f} €",
                delta_color="inverse"
            )

        # Spaziatura verticale
        st.write("") 
        
        # E. Pulsante Nuovo
        btn_label = "❌ Chiudi Form" if st.session_state.show_add_form else "➕ Nuovo Intervento"
        btn_type = "secondary" if st.session_state.show_add_form else "primary"
        
        if st.button(btn_label, type=btn_type, use_container_width=True):
            st.session_state.show_add_form = not st.session_state.show_add_form
            st.rerun()

    # --- COLONNA DESTRA: Filtri Categoria e Tabella ---
    with col_data:
        # A. Filtro Categoria (Full Width)
        # Rimosse le colonne interne per estendere il filtro a tutta la larghezza
        all_categories = sorted(list(set(r.expense_type for r in records)))
        selected_cats = st.multiselect(
            "Categoria", 
            all_categories, 
            placeholder="🔍 Filtra Categoria (Multiselezione)...",
            label_visibility="collapsed"
        )

        # B. Applicazione Filtro Categoria (sui dati già filtrati per anno)
        final_display_records = records_year_filtered
        if selected_cats:
            final_display_records = [r for r in final_display_records if r.expense_type in selected_cats]
        
        # C. Render Tabella
        if final_display_records:
            df_display = grids.build_maintenance_dataframe(final_display_records)
            st.dataframe(
                df_display.drop(columns=["_obj"]), 
                width="stretch",
                hide_index=True,
                column_config={
                    "ID": None,
                    "Descrizione": st.column_config.TextColumn(width="large"),
                    "Tipo": st.column_config.TextColumn(width="medium")
                }
            )
        else:
            if not records:
                st.info("Database vuoto.")
            else:
                st.info("Nessun dato con i filtri selezionati.")

    # ---------------------------------------------------------
    # 2. PANNELLO AGGIUNTA (A comparsa - Sotto la struttura principale)
    # ---------------------------------------------------------
    if st.session_state.show_add_form:
        st.divider()

        with st.container(border=True):
            st.markdown("##### ✨ Registra Nuovo Intervento")
            with st.form("new_maint_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                last_km_refuel = crud.get_max_km(db)
                
                m_date = c1.date_input("Data Intervento", value=date.today())
                m_km = c1.number_input("Odometro (Km)", value=last_km_refuel, step=1)
                
                m_type = c2.selectbox("Categoria", ["Tagliando", "Gomme", "Batteria", "Revisione", "Bollo", "Riparazione", "Altro"])
                m_cost = c2.number_input("Costo (€)", min_value=0.0, step=1.0, format="%.2f")
                m_desc = st.text_area("Note / Dettagli", placeholder="Es. Cambio olio Castrol 5W30...")

                # Pulsanti Form
                cf1, cf2 = st.columns([6, 1])
                if cf2.form_submit_button("Salva", type="primary", use_container_width=True):
                    if m_cost > 0:
                        crud.create_maintenance(db, m_date, m_km, m_type, m_cost, m_desc)
                        st.success("✅ Salvato!")
                        st.session_state.show_add_form = False # Chiude dopo il salvataggio
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Costo > 0 richiesto")

    st.divider()

    # ---------------------------------------------------------
    # 3. AREA GESTIONE (Modifica / Elimina Avanzata)
    # ---------------------------------------------------------
    st.subheader("🛠️ Gestione Interventi")
    
    st.markdown("""
    > **Come usare questa sezione:** 
    > Qui puoi correggere eventuali errori di inserimento o cancellare degli Interventi.  
    > 1. Seleziona l'**Anno** di riferimento.  
    > 2. Scegli lo **Specifico Intervento** dal menu a tendina.  
    > 3. Usa i pulsanti **Modifica (✏️)** o **Elimina (🗑️)** per procedere.
    """)

    if records:
        # A. Selezione Anno (Indipendente dal filtro superiore)
        years = sorted(list(set(r.date.year for r in records)), reverse=True)
        try:
            curr_year_idx = years.index(current_year)
        except ValueError:
            curr_year_idx = 0
            
        col_year, col_rec, col_act1, col_act2 = st.columns([1.5, 5, 0.7, 0.7], gap="small")
        
        selected_year = col_year.selectbox("Anno Gestione", years, index=curr_year_idx, label_visibility="collapsed", key="mgmt_year_select")
        
        records_for_year = [r for r in records if r.date.year == selected_year]
        
        if not records_for_year:
            col_rec.warning("Nessun record in questo anno.")
        else:
            rec_options = {f"{r.date.strftime('%d/%m')} - {r.expense_type} (€ {r.cost:.0f})": r.id for r in records_for_year}
            selected_label = col_rec.selectbox("Seleziona Record", list(rec_options.keys()), label_visibility="collapsed")
            
            if selected_label:
                target_id = rec_options[selected_label]
                
                if col_act1.button("✏️", help="Modifica", use_container_width=True):
                    st.session_state.active_operation = "edit"
                    st.session_state.selected_record_id = target_id
                    st.rerun() 
                
                if col_act2.button("🗑️", help="Elimina", type="primary", use_container_width=True):
                    st.session_state.active_operation = "delete"
                    st.session_state.selected_record_id = target_id
                    st.rerun()

        # ---------------------------------------------------------
        # 4. PANNELLI DINAMICI (Edit / Delete)
        # ---------------------------------------------------------
        
        if st.session_state.active_operation and st.session_state.selected_record_id:
            target_record = next((r for r in records if r.id == st.session_state.selected_record_id), None)
            
            if target_record:
                # --- PANNELLO MODIFICA ---
                if st.session_state.active_operation == "edit":
                    st.markdown(f"**Modifica Intervento del {target_record.date.strftime('%d/%m/%Y')}**")
                    with st.container(border=True):
                        with st.form("edit_dynamic_form"):
                            ce1, ce2 = st.columns(2)
                            new_date = ce1.date_input("Data", value=target_record.date)
                            new_km = ce1.number_input("Km", value=target_record.total_km, step=1)
                            
                            cat_opts = ["Tagliando", "Gomme", "Batteria", "Revisione", "Bollo", "Riparazione", "Altro"]
                            curr_idx = cat_opts.index(target_record.expense_type) if target_record.expense_type in cat_opts else 0
                            new_type = ce2.selectbox("Categoria", cat_opts, index=curr_idx)
                            new_cost = ce2.number_input("Costo", value=target_record.cost, min_value=0.0, step=1.0)
                            new_desc = st.text_area("Note", value=target_record.description)
                            
                            cb1, cb2 = st.columns([5, 1])
                            if cb2.form_submit_button("💾 Aggiorna", type="primary", use_container_width=True):
                                changes = {"date": new_date, "total_km": new_km, "expense_type": new_type, "cost": new_cost, "description": new_desc}
                                crud.update_maintenance(db, target_record.id, changes)
                                st.success("Record aggiornato!")
                                st.session_state.active_operation = None
                                st.cache_data.clear()
                                st.rerun()
                                
                        if st.button("Annulla Modifica"):
                            st.session_state.active_operation = None
                            st.rerun()

                # --- PANNELLO ELIMINAZIONE ---
                elif st.session_state.active_operation == "delete":
                    st.error(f"⚠️ Stai per eliminare definitivamente: **{target_record.expense_type}** del {target_record.date} (€ {target_record.cost}).")
                    
                    cd1, cd2, cd3 = st.columns([1, 1, 4])
                    if cd1.button("✅ Conferma", type="primary", use_container_width=True):
                        crud.delete_maintenance(db, target_record.id)
                        st.success("Eliminato.")
                        st.session_state.active_operation = None
                        st.session_state.selected_record_id = None
                        st.cache_data.clear()
                        st.rerun()
                    
                    if cd2.button("❌ Annulla", use_container_width=True):
                        st.session_state.active_operation = None
                        st.rerun()
            else:
                st.session_state.active_operation = None
                st.rerun()

    else:
        st.info("Database vuoto.")

    db.close()