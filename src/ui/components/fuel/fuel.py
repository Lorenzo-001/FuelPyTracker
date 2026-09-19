import streamlit as st
from datetime import date
from src.database.core import get_db
from src.database import crud
from src.ui.components.fuel import kpi
from src.ui.components.fuel.add_panel import render_add_panel
from src.ui.components.fuel.history_tab import render_history_tab
from src.ui.components.fuel.manage_tab import render_management_tab
from src.services.business import fuel_logic


@st.fragment
def render():
    """Vista Principale: Gestione Rifornimenti (Refactored)."""
    st.header("⛽ Gestione Rifornimenti")
    
    # --- 1. Init Stato & DB ---
    # Get utente (Salvato in main.py dopo il login)
    user = st.session_state["user"]

    if "active_operation" not in st.session_state:
        st.session_state.active_operation = None
    if "selected_record_id" not in st.session_state:
        st.session_state.selected_record_id = None

    db = next(get_db())
    all_records = crud.get_all_refuelings(db, user.id)
    last_record = crud.get_last_refueling(db, user.id)
    settings = crud.get_settings(db, user.id)
    
    # Setup Defaults
    last_km = last_record.total_km if last_record else 0
    last_price = last_record.price_per_liter if last_record else 1.650
    years = sorted(list(set(r.date.year for r in all_records)), reverse=True)
    if not years: years = [date.today().year]

    # --- 2. Top Bar & KPI ---
    # Determina indice default in modo sicuro
    def_idx = years.index(date.today().year) if date.today().year in years else 0
    view_year = st.selectbox("📅 Visualizza Anno", years, index=def_idx, key="view_year_sel")
    
    # Calcolo KPI (Delegato al service logic)
    stats = fuel_logic.calculate_year_kpis(all_records, view_year)
    
    kpi.render_fuel_cards(
        view_year, stats["total_cost"], stats["total_liters"], 
        stats["km_est"], stats["avg_price"], stats["min_eff"], stats["max_eff"]
    )

    # --- 3. Area Inserimento (ADD) ---
    range_val = settings.price_fluctuation_cents
    min_p, max_p = max(0.0, last_price - range_val), last_price + range_val

    render_add_panel(db, user, all_records, settings, last_km, last_price, min_p, max_p)

    st.write("") 

    # --- 4. Tabs: Storico & Gestione ---
    tab_list, tab_manage = st.tabs(["📋 Storico", "🛠️ Gestione"])

    # TAB A: Lista
    with tab_list:
        render_history_tab(stats["view_records"], view_year)

    # TAB B: Modifica/Elimina
    with tab_manage:
        render_management_tab(db, user, all_records, years, def_idx, settings)
    
    db.close()
