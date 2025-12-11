import streamlit as st
import pandas as pd
from datetime import date
from src.database.core import get_db
from src.database import crud
from src.ui.components import grids, kpi, forms
from src.services import fuel_logic

def render():
    """Vista Principale: Gestione Rifornimenti (Refactored)."""
    st.header("⛽ Gestione Rifornimenti")
    
    # --- 1. Init Stato & DB ---
    if "active_operation" not in st.session_state:
        st.session_state.active_operation = None
    if "selected_record_id" not in st.session_state:
        st.session_state.selected_record_id = None

    db = next(get_db())
    all_records = crud.get_all_refuelings(db)
    last_record = crud.get_last_refueling(db)
    settings = crud.get_settings(db)
    
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

    with st.expander("➕ Registra Nuovo Rifornimento", expanded=False):
        st.caption(f"Range suggerito: {min_p:.3f} - {max_p:.3f} €/L")
        with st.form("fuel_form_add", clear_on_submit=True):
            # Form delegato al componente UI
            new_data = forms.render_refueling_inputs(
                date.today(), last_km, last_price, 0.0, True, "", 
                min_p, max_p, settings.max_total_cost
            )
            
            if st.form_submit_button("Salva", type="primary", width="stretch"):
                is_valid, err_msg = fuel_logic.validate_refueling(new_data, last_km)
                if not is_valid:
                    st.error(err_msg)
                else:
                    try:
                        liters = new_data['cost'] / new_data['price']
                        crud.create_refueling(db, new_data['date'], new_data['km'], new_data['price'], 
                                            new_data['cost'], liters, new_data['full'], new_data['notes'])
                        st.success(f"✅ Salvato! ({liters:.2f} L)")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore DB: {e}")

    st.write("") 

    # --- 4. Tabs: Storico & Gestione ---
    tab_list, tab_manage = st.tabs(["📋 Storico", "🛠️ Gestione"])

    # TAB A: Lista
    with tab_list:
        _render_history_tab(stats["view_records"], view_year)

    # TAB B: Modifica/Elimina
    with tab_manage:
        _render_management_tab(db, all_records, years, def_idx, settings)
    
    db.close()

# --- Helper Functions Locali (per pulizia render principale) ---

def _render_history_tab(records, year):
    if not records:
        st.info(f"Nessun dato nel {year}.")
        return

    df = grids.build_fuel_dataframe(records)
    # Formattazione per visualizzazione
    df['Data'] = pd.to_datetime(df['Data'])
    df_show = df.copy()
    df_show['Data'] = df_show['Data'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        df_show.drop(columns=["_obj"]), 
        width="stretch", hide_index=True,
        column_config={
            "ID": None, 
            "Pieno": st.column_config.TextColumn(width="small"),
            "Km/L": st.column_config.TextColumn(width="small"),
            "Descrizione": st.column_config.TextColumn(width="medium")
        }
    )

def _render_management_tab(db, all_records, years, def_idx, settings):
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
    if c1.button("✏️ Modifica", width="stretch"):
        st.session_state.active_operation = "edit"
        st.session_state.selected_record_id = target_id
        st.rerun()
    if c2.button("🗑️ Elimina", type="primary", width="stretch"):
        st.session_state.active_operation = "delete"
        st.session_state.selected_record_id = target_id
        st.rerun()
    
    # Gestione Pannelli Operativi
    if st.session_state.active_operation and st.session_state.selected_record_id == target_id:
        target_rec = next((r for r in all_records if r.id == target_id), None)
        if target_rec:
            st.divider()
            if st.session_state.active_operation == "edit":
                _handle_edit_flow(db, target_rec, settings)
            elif st.session_state.active_operation == "delete":
                _handle_delete_flow(db, target_id)

def _handle_edit_flow(db, rec, settings):
    st.markdown(f"**Modifica Record:** {rec.date}")
    with st.form("fuel_form_edit"):
        min_pe, max_pe = max(0.0, rec.price_per_liter-0.5), rec.price_per_liter+0.5
        
        # Riutilizzo componente UI form
        edit_data = forms.render_refueling_inputs(
            rec.date, rec.total_km, rec.price_per_liter, rec.total_cost, 
            rec.is_full_tank, rec.notes, min_pe, max_pe, settings.max_total_cost
        )
        
        if st.form_submit_button("Aggiorna", type="primary", width="stretch"):
            # Nota: In edit non controlliamo "last_km" stretto come in insert per flessibilità
            new_liters = edit_data['cost'] / edit_data['price'] if edit_data['price'] > 0 else 0
            changes = {
                "date": edit_data['date'], "total_km": edit_data['km'], 
                "price_per_liter": edit_data['price'], "total_cost": edit_data['cost'], 
                "liters": new_liters, "is_full_tank": edit_data['full'], "notes": edit_data['notes']
            }
            crud.update_refueling(db, rec.id, changes)
            st.success("Record aggiornato!"); st.session_state.active_operation = None; st.rerun()
            
    if st.button("Annulla", width="stretch"):
        st.session_state.active_operation = None; st.rerun()

def _handle_delete_flow(db, record_id):
    st.error("Sei sicuro di voler eliminare definitivamente questo record?")
    cd1, cd2 = st.columns(2)
    if cd1.button("Sì, Elimina", type="primary", width="stretch"):
        crud.delete_refueling(db, record_id)
        st.success("Eliminato."); st.session_state.active_operation = None; st.rerun()
    if cd2.button("No, Annulla", width="stretch"):
        st.session_state.active_operation = None; st.rerun()