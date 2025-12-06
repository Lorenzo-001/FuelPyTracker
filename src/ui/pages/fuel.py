import streamlit as st
import pandas as pd
from datetime import date
from database.core import get_db
from database import crud
from ui.components import grids
from services.calculations import calculate_stats
def render():
    st.header("⛽ Gestione Rifornimenti")
    
    st.write("") 
    st.write("")

    # Inizializzazione Stato
    if "active_operation" not in st.session_state:
        st.session_state.active_operation = None
    if "selected_record_id" not in st.session_state:
        st.session_state.selected_record_id = None

    db = next(get_db())
    
    # Recupero Dati e Contesti Globale
    all_records = crud.get_all_refuelings(db)
    last_record = crud.get_last_refueling(db)
    settings = crud.get_settings(db)
    
    last_km = last_record.total_km if last_record else 0
    last_price = last_record.price_per_liter if last_record else 1.650

    # Preparazione Anni (Globale)
    years = sorted(list(set(r.date.year for r in all_records)), reverse=True)
    if not years: years = [date.today().year]
    current_year = date.today().year
    
    try:
        default_idx = years.index(current_year)
    except ValueError:
        default_idx = 0

    # ---------------------------------------------------------
    # 1. TOOLBAR E KPI (Layout Asimmetrico)
    # ---------------------------------------------------------
    col_ctrl, col_data = st.columns([1, 2.5], gap="medium")

    # Variabile per contenere i record filtrati per visualizzazione
    view_records = []

    # --- COLONNA SINISTRA: Controlli e KPI ---
    with col_ctrl:
        # A. Selectbox Unificata (fuori dal container grafico per pulizia, o dentro se preferisci)
        view_year = st.selectbox(
            "📅 Visualizza Anno", 
            years, 
            index=default_idx, 
            key="view_year_sel"
        )
        
        # Filtro Record SOLO per calcolo KPI (qui va bene filtrare)
        view_records_kpi = [r for r in all_records if r.date.year == view_year]

        # B. Calcolo KPI Avanzati (Codice invariato, serve per i calcoli)
        total_liters = 0
        total_cost = 0.0
        km_driven_est = 0
        avg_price = 0.0
        worst_efficiency = 0.0 
        best_efficiency = 0.0  

        if view_records_kpi:
            total_liters = sum(r.liters for r in view_records_kpi)
            total_cost = sum(r.total_cost for r in view_records_kpi)
            
            if total_liters > 0:
                avg_price = total_cost / total_liters
            
            if len(view_records_kpi) > 1:
                # Stima KM: Max - Min nell'anno selezionato
                km_vals = [r.total_km for r in view_records_kpi]
                km_driven_est = max(km_vals) - min(km_vals)
            
            # Calcolo efficienza (usando all_records per avere i delta corretti)
            efficiencies = []
            for r in view_records_kpi:
                stats = calculate_stats(r, all_records)
                if stats["km_per_liter"]:
                    efficiencies.append(stats["km_per_liter"])
            
            if efficiencies:
                worst_efficiency = min(efficiencies) # Min Km/L = Peggior resa
                best_efficiency = max(efficiencies)  # Max Km/L = Miglior resa

        # C. Visualizzazione KPI (Restyling Grafico)
        with st.container(border=True):
            st.markdown(f"### 📊 Riepilogo {view_year}")
            
            # 1. CARD SPESA (Custom HTML per risalto)
            st.markdown(f"""
            <div style="
                background-color: #f0f2f6; 
                padding: 15px; 
                border-radius: 8px; 
                border-left: 5px solid #ff4b4b; 
                margin-bottom: 20px;">
                <p style="margin:0; font-size: 14px; color: #555;">💰 Spesa Totale</p>
                <h2 style="margin:0; font-size: 28px; color: #31333F;">{total_cost:.2f} €</h2>
                <p style="margin:0; font-size: 14px; color: #666;">⛽ <b>{total_liters:.1f}</b> Litri erogati</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 2. Statistiche Generali
            k1, k2 = st.columns(2)
            k1.metric("🛣️ Km Stimati", value=f"{km_driven_est}", help="Differenza Km inizio/fine anno")
            k2.metric("🏷️ Media €/L", value=f"{avg_price:.3f} €")
            
            st.markdown("---") # Divisore sottile
            
            # 3. Efficienza (Rinominato per chiarezza)
            st.caption("🏎️ Performance Motore")
            e1, e2 = st.columns(2)
            
            # Peggior Resa (Min Km/L)
            e1.metric(
                "📉 Minima", 
                value=f"{worst_efficiency:.1f} Km/L", 
                help="Il minimo dei Km percorsi con un litro"
            )
            
            # Miglior Resa (Max Km/L)
            e2.metric(
                "📈 Massima", 
                value=f"{best_efficiency:.1f} Km/L",
                help="Il massimo dei Km percorsi con un litro"
            )

    # --- COLONNA DESTRA: Area Inserimento ---
    with col_data:
        # Calcolo range per NUOVO inserimento
        range_val = settings.price_fluctuation_cents
        min_price_allow = max(0.0, last_price - range_val)
        max_price_allow = last_price + range_val

        with st.expander("⛽ Registra Nuovo Rifornimento", expanded=True):
            st.caption(f"💡 Range prezzi suggerito: **{min_price_allow:.3f}** - **{max_price_allow:.3f}** €/L")
            
            with st.form("fuel_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                d_date = c1.date_input("Data", value=date.today())
                d_km = c1.number_input("Odometro (Km)", value=last_km, step=1, format="%d")
                
                d_price = c2.slider(
                    "Prezzo (€/L)", 
                    min_value=float(f"{min_price_allow:.3f}"), 
                    max_value=float(f"{max_price_allow:.3f}"), 
                    value=float(f"{last_price:.3f}"), 
                    step=0.001, format="%.3f"
                )

                d_cost = c2.number_input("Totale (€)", min_value=0.0, max_value=settings.max_total_cost, step=0.01, format="%.2f")
                
                d_full = st.checkbox("Pieno Completato?", value=True)
                d_notes = st.text_area("Note")
                
                # Pulsante Salva (Allineato a destra)
                cf1, cf2 = st.columns([5, 1])
                if cf2.form_submit_button("Salva", type="primary", use_container_width=True):
                    _handle_submit(db, d_date, d_km, last_km, d_price, d_cost, d_full, d_notes)

    st.write("")

    # ---------------------------------------------------------
    # 3. TABELLA DATI
    # ---------------------------------------------------------
    if all_records:
        # Generiamo il DataFrame su TUTTI i dati per avere i delta corretti
        df_full = grids.build_fuel_dataframe(all_records)
        
        # ORA filtriamo il DataFrame per visualizzare solo l'anno scelto
        df_full['Data'] = pd.to_datetime(df_full['Data'])
        df_display = df_full[df_full['Data'].dt.year == view_year].copy()
        
        # Formattiamo la data per la visualizzazione
        df_display['Data'] = df_display['Data'].dt.strftime('%Y-%m-%d')
        if not df_display.empty:
            # Mostra il più recente in alto
            # Se build_fuel_dataframe mantiene l'ordine di 'all_records' (che è DESC), siamo già a posto.
            # Se necessario, forziamo l'ordine qui.
            st.dataframe(
                df_display.drop(columns=["_obj"]), 
                width="stretch", 
                hide_index=True,
                column_config={
                    "ID": None, 
                    "Pieno": st.column_config.TextColumn(width="small"),
                    "Km/L": st.column_config.TextColumn(help="Calcolato su pieno completo"),
                    "Descrizione": st.column_config.TextColumn(width="large")
                }
            )
        else:
            st.info(f"Nessun rifornimento da mostrare nel {view_year}.")
    else:
        st.info("Database vuoto.")
    
    st.divider()

    # ---------------------------------------------------------
    # 4. AREA GESTIONE (Modifica / Elimina)
    # ---------------------------------------------------------
    st.subheader("🛠️ Gestione Rifornimenti")
    
    st.markdown("""
    > **Come usare questa sezione:**
    > 1. Seleziona l'**Anno di Gestione** (indipendente dalla tabella sopra).  
    > 2. Scegli il **Rifornimento** dal menu.  
    > 3. Usa i pulsanti **Modifica (✏️)** o **Elimina (🗑️)**.
    """)

    if all_records:
        # A. Selezione Anno GESTIONE (Indipendente)
        col_year_mgmt, col_rec_mgmt, col_act1, col_act2 = st.columns([1.5, 5, 0.7, 0.7], gap="small")
        
        # Cerchiamo di preselezionare l'anno corrente o il primo disponibile
        try:
            curr_idx = years.index(current_year)
        except ValueError:
            curr_idx = 0

        mgmt_year = col_year_mgmt.selectbox("Anno Gestione", years, index=curr_idx, label_visibility="collapsed", key="mgmt_year_sel")
        
        # Filtriamo i record per la gestione
        mgmt_records = [r for r in all_records if r.date.year == mgmt_year]
        
        if not mgmt_records:
            col_rec_mgmt.warning("Nessun record modificabile in questo anno.")
        else:
            # B. Selezione Record
            rec_options = {f"{r.date.strftime('%d/%m')} - {r.total_km} km (€ {r.total_cost:.2f})": r.id for r in mgmt_records}
            selected_label = col_rec_mgmt.selectbox("Seleziona Record", list(rec_options.keys()), label_visibility="collapsed")
            
            if selected_label:
                target_id = rec_options[selected_label]
                
                # C. Pulsanti Full Width
                if col_act1.button("✏️", key="btn_edit_fuel", help="Modifica", use_container_width=True):
                    st.session_state.active_operation = "edit"
                    st.session_state.selected_record_id = target_id
                    st.rerun()
                
                if col_act2.button("🗑️", key="btn_del_fuel", help="Elimina", type="primary", use_container_width=True):
                    st.session_state.active_operation = "delete"
                    st.session_state.selected_record_id = target_id
                    st.rerun()

        # ---------------------------------------------------------
        # 4. PANNELLI DINAMICI
        # ---------------------------------------------------------
        if st.session_state.active_operation and st.session_state.selected_record_id:
            target_record = next((r for r in all_records if r.id == st.session_state.selected_record_id), None)
            
            if target_record:
                # --- MODIFICA ---
                if st.session_state.active_operation == "edit":
                    st.write("")
                    st.markdown(f"**Modifica Rifornimento del {target_record.date.strftime('%d/%m/%Y')}**")
                    with st.container(border=True):
                        with st.form("edit_fuel_dynamic"):
                            ce1, ce2 = st.columns(2)
                            new_date = ce1.date_input("Data", value=target_record.date)
                            new_km = ce1.number_input("Odometro (Km)", value=target_record.total_km, step=1)
                            
                            # Logica Slider per Edit
                            curr_p = target_record.price_per_liter
                            p_min = max(0.0, curr_p - 0.50)
                            p_max = curr_p + 0.50
                            
                            new_price = ce2.slider(
                                "Prezzo (€/L)", 
                                min_value=float(f"{p_min:.3f}"), 
                                max_value=float(f"{p_max:.3f}"), 
                                value=float(f"{curr_p:.3f}"), 
                                step=0.001, format="%.3f"
                            )
                            
                            # Costo modificabile
                            new_cost = ce2.number_input(
                                "Totale (€)", 
                                value=target_record.total_cost, 
                                min_value=0.0, 
                                max_value=settings.max_total_cost, 
                                step=0.01, format="%.2f"
                            )
                            
                            new_full = st.checkbox("Pieno?", value=target_record.is_full_tank)
                            new_notes = st.text_area("Note", value=target_record.notes)
                            
                            cb1, cb2 = st.columns([5, 1])
                            if cb2.form_submit_button("💾 Aggiorna", type="primary", use_container_width=True):
                                # Ricalcolo litri
                                new_liters = new_cost / new_price if new_price > 0 else 0
                                changes = {
                                    "date": new_date, "total_km": new_km, 
                                    "price_per_liter": new_price, "total_cost": new_cost, 
                                    "liters": new_liters, "is_full_tank": new_full, "notes": new_notes
                                }
                                # Sandwich Validation
                                neighbors = crud.get_neighbors(db, new_date)
                                
                                err_msg = None
                                if neighbors['prev'] and neighbors['prev'].id != target_id and new_km <= neighbors['prev'].total_km:
                                    err_msg = f"⛔ Errore: Km ({new_km}) <= Precedente ({neighbors['prev'].total_km})."
                                elif neighbors['next'] and neighbors['next'].id != target_id and new_km >= neighbors['next'].total_km:
                                    err_msg = f"⛔ Errore: Km ({new_km}) >= Successivo ({neighbors['next'].total_km})."
                                
                                if err_msg:
                                    st.error(err_msg)
                                else:
                                    crud.update_refueling(db, target_record.id, changes)
                                    st.success("Aggiornato!")
                                    st.session_state.active_operation = None
                                    st.cache_data.clear()
                                    st.rerun()
                        
                        if st.button("Annulla Modifica"):
                            st.session_state.active_operation = None
                            st.rerun()

                # --- ELIMINAZIONE ---
                elif st.session_state.active_operation == "delete":
                    st.write("")
                    with st.container(border=True):
                        st.error(f"Eliminare il rifornimento del {target_record.date} ({target_record.total_km} km)?")
                        st.caption("Attenzione: rimuovere un pieno intermedio potrebbe alterare i calcoli di consumo dei record successivi.")
                        
                        cd1, cd2, cd3 = st.columns([1, 1, 4])
                        if cd1.button("✅ Conferma", type="primary", use_container_width=True):
                            crud.delete_refueling(db, target_record.id)
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

def _handle_submit(db, d_date, d_km, last_km, d_price, d_cost, d_full, d_notes):
    if d_date >= date.today() and d_km < last_km:
        st.error(f"⛔ Errore Km: non puoi inserire {d_km} km se l'ultimo era {last_km}.")
        return
    
    if d_price <= 0 or d_cost <= 0:
        st.error("Valori non validi.")
        return

    try:
        liters = d_cost / d_price
        crud.create_refueling(db, d_date, d_km, d_price, d_cost, liters, d_full, d_notes)
        st.success(f"✅ Rifornimento salvato! ({liters:.2f} L)")
        st.cache_data.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Errore DB: {e}")