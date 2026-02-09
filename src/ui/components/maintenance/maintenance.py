import streamlit as st
from datetime import date
from src.database.core import get_db
from src.database import crud
from src.services.business import maintenance_logic
from src.services.business.prediction import calculate_daily_usage_rate
from src.ui.components.maintenance import add_form, cards, tabs, kpi, reminders_ui

@st.fragment
def render():
    """Vista Principale: Registro Manutenzioni (Refactored & Multi-Tenant)."""
    st.header("🔧 Registro Manutenzioni")
    
    # --- 1. Init Stato & DB ---
    _init_session_state()
    user = st.session_state["user"]

    db = next(get_db())
    records = crud.get_all_maintenances(db, user.id)
    refuelings = crud.get_all_refuelings(db, user.id)
    
    # Recuperiamo l'ultimo km noto (fondamentale per i Reminder)
    last_km = max(r.total_km for r in refuelings) if refuelings else 0
    
    # --- 2. Top Bar & Filtri Globali ---
    db_years = maintenance_logic.get_available_years(records)
    year_options = ["Tutti gli anni"] + db_years
    curr_year = date.today().year
    def_idx = db_years.index(curr_year) + 1 if curr_year in db_years else 0
    
    c_year, c_kpi, c_btn = st.columns([1.5, 1.5, 1.2], gap="small", vertical_alignment="bottom")
    
    with c_year:
        sel_year_opt = st.selectbox("📅 Anno Riferimento", year_options, index=def_idx, key="maint_year_filter")

    recs_filtered, label_kpi = maintenance_logic.filter_records_by_year(records, sel_year_opt)
    total_spent = sum(r.cost for r in recs_filtered)

    with c_kpi:
        kpi.render_maintenance_card(total_spent, label_kpi)

    with c_btn:
        _render_add_button()

    # --- 3. Area Inserimento ---
    if st.session_state.show_add_form:
        add_form.render_add_form(db, user)

    st.write("") 

    # --- 4. TABS ---
    tab_hist, tab_mgmt, tab_deadlines, tab_reminders = st.tabs(["📋 Storico", "🛠️ Gestione", "🔮 Scadenze", "⏰ Promemoria"])

    with tab_deadlines:
        if refuelings and records:
            daily_rate = calculate_daily_usage_rate(refuelings)
            last_km = max(r.total_km for r in refuelings) if refuelings else 0
            cards.render_predictive_section(db, user, records, last_km, daily_rate)
        else:
            st.info("Inserisci almeno 2 rifornimenti e una manutenzione con scadenza per vedere le previsioni.")

    with tab_hist:
        tabs.render_history_tab(recs_filtered, records)

    with tab_mgmt:
        tabs.render_management_tab(db, user, records)
        
    with tab_reminders:
        reminders_ui.render_tab(db, user, last_km)

    db.close()

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