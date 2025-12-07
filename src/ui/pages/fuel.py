import streamlit as st
import pandas as pd
from datetime import date
from database.core import get_db
from database import crud
from ui.components import grids, kpi
from services.calculations import calculate_stats

def render():
    st.header("⛽ Gestione Rifornimenti")
    
    # --- INIT STATE ---
    if "active_operation" not in st.session_state:
        st.session_state.active_operation = None
    if "selected_record_id" not in st.session_state:
        st.session_state.selected_record_id = None

    db = next(get_db())
    all_records = crud.get_all_refuelings(db)
    last_record = crud.get_last_refueling(db)
    settings = crud.get_settings(db)
    
    # Defaults
    last_km = last_record.total_km if last_record else 0
    last_price = last_record.price_per_liter if last_record else 1.650

    # Gestione Anni
    years = sorted(list(set(r.date.year for r in all_records)), reverse=True)
    if not years: years = [date.today().year]
    try:
        default_idx = years.index(date.today().year)
    except ValueError:
        default_idx = 0

    # --- TOP BAR: SELETTORE ANNO ---
    view_year = st.selectbox("📅 Visualizza Anno", years, index=default_idx, key="view_year_sel")
    
    # --- DATA PREPARATION PER KPI ---
    view_records = [r for r in all_records if r.date.year == view_year]
    
    # Aggregazione dati (Logica invariata)
    total_liters = sum(r.liters for r in view_records)
    total_cost = sum(r.total_cost for r in view_records)
    avg_price = (total_cost / total_liters) if total_liters > 0 else 0.0
    
    km_est = 0
    if len(view_records) > 1:
        km_vals = [r.total_km for r in view_records]
        km_est = max(km_vals) - min(km_vals)
    
    efficiencies = [
        stats["km_per_liter"] 
        for r in view_records 
        if (stats := calculate_stats(r, all_records))["km_per_liter"]
    ]
    min_eff = min(efficiencies) if efficiencies else 0.0
    max_eff = max(efficiencies) if efficiencies else 0.0

    # --- RENDER KPI (Delegato al componente) ---
    kpi.render_fuel_cards(view_year, total_cost, total_liters, km_est, avg_price, min_eff, max_eff)

    # --- AREA INSERIMENTO (ADD) ---
    range_val = settings.price_fluctuation_cents
    min_p, max_p = max(0.0, last_price - range_val), last_price + range_val

    with st.expander("➕ Registra Nuovo Rifornimento", expanded=False):
        st.caption(f"Range suggerito: {min_p:.3f} - {max_p:.3f} €/L")
        with st.form("fuel_form_add", clear_on_submit=True):
            # Usiamo l'helper per generare i campi
            data = _render_form_fields(date.today(), last_km, last_price, 0.0, True, "", min_p, max_p, settings.max_total_cost)
            
            if st.form_submit_button("Salva", type="primary", width="stretch"):
                 _handle_submit(db, data, last_km)

    st.write("") 

    # --- TABS: TABELLA & GESTIONE ---
    tab_list, tab_manage = st.tabs(["📋 Storico", "🛠️ Gestione"])

    with tab_list:
        if all_records:
            df = grids.build_fuel_dataframe(all_records)
            df['Data'] = pd.to_datetime(df['Data'])
            df_show = df[df['Data'].dt.year == view_year].copy()
            df_show['Data'] = df_show['Data'].dt.strftime('%Y-%m-%d')
            
            if not df_show.empty:
                st.dataframe(
                    df_show.drop(columns=["_obj"]), 
                    width="stretch", hide_index=True,
                    column_config={
                        "ID": None, "Pieno": st.column_config.TextColumn(width="small"),
                        "Km/L": st.column_config.TextColumn(width="small"),
                        "Descrizione": st.column_config.TextColumn(width="medium")
                    }
                )
            else:
                st.info(f"Nessun dato nel {view_year}.")
        else:
            st.info("Nessun dato.")

    with tab_manage:
        if all_records:
            # Selezione record per edit/delete
            mgmt_year = st.selectbox("Anno Gestione", years, index=default_idx, key="mgmt_year_sel")
            recs_year = [r for r in all_records if r.date.year == mgmt_year]
            
            if recs_year:
                opts = {f"{r.date.strftime('%d/%m')} - {r.total_km}km (€ {r.total_cost:.2f})": r.id for r in recs_year}
                sel_label = st.selectbox("Seleziona Record", list(opts.keys()))
                target_id = opts[sel_label] if sel_label else None
                
                c1, c2 = st.columns(2)
                if c1.button("✏️ Modifica", width="stretch"):
                    st.session_state.active_operation = "edit"
                    st.session_state.selected_record_id = target_id
                    st.rerun()
                if c2.button("🗑️ Elimina", type="primary", width="stretch"):
                    st.session_state.active_operation = "delete"
                    st.session_state.selected_record_id = target_id
                    st.rerun()
                
                # Pannelli dinamici Edit/Delete
                if st.session_state.active_operation and st.session_state.selected_record_id == target_id:
                    rec = next((r for r in all_records if r.id == target_id), None)
                    if rec:
                        st.divider()
                        if st.session_state.active_operation == "edit":
                            st.markdown(f"**Modifica:** {rec.date}")
                            with st.form("fuel_form_edit"):
                                # Riutilizzo l'helper pre-compilando i campi con i dati del record
                                min_pe, max_pe = max(0.0, rec.price_per_liter-0.5), rec.price_per_liter+0.5
                                data_edit = _render_form_fields(rec.date, rec.total_km, rec.price_per_liter, rec.total_cost, rec.is_full_tank, rec.notes, min_pe, max_pe, settings.max_total_cost)
                                
                                if st.form_submit_button("Aggiorna", type="primary", width="stretch"):
                                    # Update logic
                                    new_liters = data_edit['cost'] / data_edit['price'] if data_edit['price'] > 0 else 0
                                    changes = {
                                        "date": data_edit['date'], "total_km": data_edit['km'], 
                                        "price_per_liter": data_edit['price'], "total_cost": data_edit['cost'], 
                                        "liters": new_liters, "is_full_tank": data_edit['full'], "notes": data_edit['notes']
                                    }
                                    crud.update_refueling(db, target_id, changes)
                                    st.success("Aggiornato!"); st.session_state.active_operation = None; st.rerun()
                                    
                            if st.button("Annulla", width="stretch"):
                                st.session_state.active_operation = None; st.rerun()

                        elif st.session_state.active_operation == "delete":
                            st.error("Eliminare definitivamente?")
                            cd1, cd2 = st.columns(2)
                            if cd1.button("Sì", type="primary", width="stretch"):
                                crud.delete_refueling(db, target_id)
                                st.success("Eliminato."); st.session_state.active_operation = None; st.rerun()
                            if cd2.button("No", width="stretch"):
                                st.session_state.active_operation = None; st.rerun()
            else:
                st.warning("Nessun record modificabile.")
    
    db.close()

# --- HELPER FUNCTIONS (Internal) ---

def _render_form_fields(def_date, def_km, def_price, def_cost, def_full, def_notes, min_p, max_p, max_cost):
    """Genera i campi standard del form per evitare duplicazioni di codice UI"""
    c1, c2 = st.columns(2)
    d_date = c1.date_input("Data", value=def_date)
    d_km = c1.number_input("Odometro", value=def_km, step=1, format="%d")
    d_price = c2.slider("Prezzo €/L", float(f"{min_p:.3f}"), float(f"{max_p:.3f}"), float(f"{def_price:.3f}"), 0.001, format="%.3f")
    d_cost = c2.number_input("Totale €", 0.0, float(max_cost), float(f"{def_cost:.2f}"), 0.01, format="%.2f")
    d_full = st.checkbox("Pieno Completato?", value=def_full)
    d_notes = st.text_area("Note", value=def_notes, height=80)
    
    return {
        "date": d_date, "km": d_km, "price": d_price, 
        "cost": d_cost, "full": d_full, "notes": d_notes
    }

def _handle_submit(db, data, last_km):
    """Gestisce il salvataggio di un NUOVO record"""
    if data['date'] >= date.today() and data['km'] < last_km:
        st.error(f"⛔ Errore Km: impossibile inserire {data['km']} se ultimo era {last_km}.")
        return
    if data['price'] <= 0 or data['cost'] <= 0:
        st.error("Valori non validi.")
        return
    try:
        liters = data['cost'] / data['price']
        crud.create_refueling(db, data['date'], data['km'], data['price'], data['cost'], liters, data['full'], data['notes'])
        st.success(f"✅ Salvato! ({liters:.2f} L)")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Errore DB: {e}")