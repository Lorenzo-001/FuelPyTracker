import streamlit as st
from datetime import date
from src.database.core import get_db
from src.database import crud
from src.ui.components import grids, kpi, forms
from src.services.business import maintenance_logic
from src.services.business.prediction import calculate_daily_usage_rate, predict_reach_date

@st.fragment
def render():
    """Vista Principale: Registro Manutenzioni (Refactored & Multi-Tenant)."""
    st.header("🔧 Registro Manutenzioni")
    
    # --- 1. Init Stato & DB ---
    _init_session_state()
    user = st.session_state["user"]

    db = next(get_db())
    records = crud.get_all_maintenances(db, user.id)
    
    # Recuperiamo i rifornimenti per il calcolo predittivo
    refuelings = crud.get_all_refuelings(db, user.id)
    
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

    st.write("") 

    # --- 4. TABS: SCADENZE - STORICO - GESTIONE ---
    tab_hist, tab_deadlines, tab_mgmt = st.tabs(["📋 Storico", "🔮 Scadenze", "🛠️ Gestione"])

    with tab_deadlines:
        # Calcolo dati predittivi solo se necessari (Lazy)
        if refuelings and records:
            daily_rate = calculate_daily_usage_rate(refuelings)
            last_km = max(r.total_km for r in refuelings) if refuelings else 0
            _render_predictive_section(records, last_km, daily_rate)
        else:
            st.info("Inserisci almeno 2 rifornimenti e una manutenzione con scadenza per vedere le previsioni.")

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
                # --- VALIDAZIONI ---
                if data['cost'] < 0:
                    st.error("Inserire un costo valido.")
                elif data['expiry_km'] and data['expiry_km'] <= data['km']:
                    st.error(f"⚠️ Errore Logico: La scadenza ({data['expiry_km']} km) deve essere maggiore dei km attuali ({data['km']} km).")
                elif data['expiry_date'] and data['expiry_date'] <= data['date']:
                    st.error("⚠️ Errore Logico: La data di scadenza deve essere successiva alla data dell'intervento.")
                else:
                    # Salvataggio
                    crud.create_maintenance(
                        db, user.id,
                        data['date'],
                        data['km'],
                        data['type'],
                        data['cost'],
                        data['desc'],
                        expiry_km=data['expiry_km'],
                        expiry_date=data['expiry_date']
                    )
                    st.success("✅ Salvato!")
                    st.session_state.show_add_form = False
                    st.cache_data.clear()
                    st.rerun()

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
        d_edit = forms.render_maintenance_inputs(
            rec.date,
            rec.total_km,
            rec.expense_type,
            rec.cost,
            rec.description,
            default_expiry_km=rec.expiry_km,
            default_expiry_date=rec.expiry_date
        )
        
        if st.form_submit_button("Aggiorna", type="primary", width="stretch"):
            # --- VALIDAZIONI ---
            if d_edit['cost'] < 0:
                st.error("Inserire un costo valido.")
            elif d_edit['expiry_km'] and d_edit['expiry_km'] <= d_edit['km']:
                st.error(f"⚠️ Errore Logico: La scadenza ({d_edit['expiry_km']} km) deve essere maggiore dei km attuali ({d_edit['km']} km).")
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
        
def _render_predictive_section(records, last_known_km, daily_rate):
    # 1. Trova tutti i candidati
    candidates = []
    
    for r in records:
        exp_km = getattr(r, 'expiry_km', None)
        exp_date = getattr(r, 'expiry_date', None)

        # Calcoliamo rimanenza
        km_left = (exp_km - last_known_km) if (exp_km and exp_km > last_known_km) else None
        days_left = (exp_date - date.today()).days if (exp_date and exp_date >= date.today()) else None
        
        # Se è una scadenza futura valida
        if km_left is not None or days_left is not None:
            candidates.append({
                "record": r,
                "km_left": km_left,
                "days_left": days_left,
                # Usiamo questo valore per capire quale scade prima (priorità ai giorni per sorting misto)
                "sort_val": km_left if km_left is not None else (days_left * 50) 
            })

    # 2. DEDUPLICAZIONE: Raggruppa per Tipo e tieni solo il più vicino
    # Questo risolve il bug della "Revisione duplicata"
    unique_upcoming = {}
    for c in candidates:
        m_type = c["record"].expense_type
        
        # Se non c'è ancora o questo scade prima del precedente salvato -> sostituisci
        if m_type not in unique_upcoming:
            unique_upcoming[m_type] = c
        else:
            if c["sort_val"] < unique_upcoming[m_type]["sort_val"]:
                unique_upcoming[m_type] = c
    
    # Convertiamo in lista
    final_upcoming = list(unique_upcoming.values())
    
    if not final_upcoming:
        st.success("✅ Nessuna scadenza imminente! Sei in regola con la manutenzione.")
        return

    st.caption(f"Stima basata su un utilizzo medio di **{daily_rate:.1f} km/giorno**.")
    st.write("")    
    
    # 3. Visualizzazione
    cols = st.columns(3)
    for idx, item_data in enumerate(final_upcoming):
        item = item_data["record"]
        col = cols[idx % 3]
        
        with col:
            with st.container(border=True):
                icon = "🔧"
                if "Gomme" in item.expense_type: icon = "🛞"
                elif "Revisione" in item.expense_type: icon = "📋"
                elif "Assicurazione" in item.expense_type: icon = "📄"
                elif "Bollo" in item.expense_type: icon = "💰"
                
                st.markdown(f"**{icon} {item.expense_type}**")
                
                km_left = item_data["km_left"]
                days_left = item_data["days_left"]

                # A. SCADENZA CHILOMETRICA
                if km_left is not None:
                    st.caption(f"Scadenza: {item.expiry_km} Km")
                    st.markdown(f"📉 **Tra {km_left} Km**")
                    
                    if daily_rate > 0:
                        est_date = predict_reach_date(last_known_km, item.expiry_km, daily_rate)
                        if est_date:
                            st.markdown(f"<span style='color:#3498db; font-size:0.9em'>📅 Stima: {est_date.strftime('%d/%m/%y')}</span>", unsafe_allow_html=True)
                
                elif days_left is not None:
                    st.caption(f"Scadenza: {item.expiry_date.strftime('%d/%m')}")
                    if days_left <= 30:
                        st.markdown(f"<span style='color:#e74c3c; font-weight:bold'>⚠️ Tra {days_left} Giorni</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"📅 **Tra {days_left} Giorni**")