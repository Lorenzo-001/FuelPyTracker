import streamlit as st
import pandas as pd
from datetime import date
from src.database.core import get_db
from src.database import crud
from src.ui.components.fuel import grids, kpi, forms
from src.services.business import fuel_logic
from src.services.ocr import process_receipt_image
from src.services.ocr.engine import is_openai_enabled

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

    with st.expander("➕ Registra Nuovo Rifornimento", expanded=False):
        
        # === A. LOGICA SMART SCAN (OCR MODAL) ===
        # Inizializziamo la "bozza" OCR se non esiste
        if "ocr_draft" not in st.session_state:
            st.session_state.ocr_draft = {}

        # Bottone Grande invece di Expander annidato
        st.markdown("##### 📸 Vuoi velocizzare l'inserimento?")
        if is_openai_enabled():
            # CASO POSITIVO: Mostra il bottone normale
            if st.button("🚀 SCANSIONA SCONTRINO CON AI", type="primary", width='stretch'):
                _open_ocr_dialog()
        else:
            # CASO NEGATIVO: Mostra bottone disabilitato o avviso
            st.button("🚀 SCANSIONA SCONTRINO (Non disponibile)", disabled=True, width='stretch', help="Funzionalità disabilitata: API Key OpenAI mancante.")
            st.caption("⚠️ Configura la chiave OpenAI nei settings per abilitare l'AI.")

        # === B. CALCOLO DEFAULTS ===
        # Se abbiamo dati in bozza (da OCR), usiamo quelli. Altrimenti storici.
        draft = st.session_state.ocr_draft
        
        # Priorità: OCR Draft -> Storico/Default
        def_date = draft.get("date", date.today())
        def_price = draft.get("price", last_price)
        def_cost = draft.get("cost", 0.0)
        
        # I KM di default sono None (vuoto) per forzare l'inserimento,
        # ma passiamo last_km come informazione per il tooltip.
        def_km = None 

        st.caption(f"Range suggerito: {min_p:.3f} - {max_p:.3f} €/L")
        
        with st.form("fuel_form_add", clear_on_submit=False):
            # Form delegato al componente UI, passando i defaults dinamici e l'ultimo KM noto per tooltip
            new_data = forms.render_refueling_inputs(
                def_date, def_km, def_price, def_cost, True, "", 
                min_p, max_p, settings.max_total_cost,
                last_km_known=last_km # Passiamo il dato per il tooltip
            )
            
            if st.form_submit_button("Salva", type="primary", width="stretch"):
                # Validazione KM: deve essere > 0 e >= last_km
                if new_data['km'] == 0:
                    st.error("⛔ Inserisci il valore dell'Odometro!")
                else:
                    is_valid, err_msg = fuel_logic.validate_refueling(new_data, all_records)
                    if not is_valid:
                        st.error(err_msg)
                    else:
                        try:
                            liters = new_data['cost'] / new_data['price']
                            crud.create_refueling(db, user.id, new_data['date'], new_data['km'], new_data['price'], 
                                                new_data['cost'], liters, new_data['full'], new_data['notes'])
                            
                            st.success(f"✅ Salvato! ({liters:.2f} L)")
                            
                            # PULIZIA: Reset della bozza OCR dopo salvataggio
                            st.session_state.ocr_draft = {}
                            
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
        _render_management_tab(db, user, all_records, years, def_idx, settings)
    
    db.close()

# --- Helper Functions Locali (per pulizia render principale) ---

@st.dialog("📸 Scansione Smart Scontrino")
def _open_ocr_dialog():
    """
    Gestisce l'UI per lo Smart Scan all'interno di un MODAL POP-UP.
    """
    st.info("Carica una foto dello scontrino. L'Intelligenza Artificiale compilerà i campi per te.")
    st.info("💡 CONSIGLIO: Assicurati che la foto sia **ben illuminata** e **a fuoco**. Se l'immagine è sfuocata o buia, l'AI potrebbe leggere numeri errati.")

    c_cam, c_upl = st.tabs(["📷 Fotocamera", "📂 Carica File"])
    img_buffer = None
    
    with c_cam:
        cam_pic = st.camera_input("Scatta foto")
        if cam_pic: img_buffer = cam_pic
    
    with c_upl:
        upl_pic = st.file_uploader("Carica immagine", type=['png', 'jpg', 'jpeg'], key="ocr_upl")
        if upl_pic: img_buffer = upl_pic

    if img_buffer:
        if st.button("✨ Analizza Ora", type="primary", width='stretch'):
            with st.spinner("Analisi AI in corso..."):
                # Chiamata al servizio
                data = process_receipt_image(img_buffer)
                
                if data.total_cost > 0:
                    # Salviamo i risultati nello stato per precompilare il form
                    st.session_state.ocr_draft = {
                        "date": data.date if data.date else date.today(),
                        "price": data.price_per_liter,
                        "cost": data.total_cost
                    }
                    st.success("Dati estratti con successo!")
                    st.rerun() # Chiude il modale e aggiorna la pagina sotto
                else:
                    st.error("Non sono riuscito a leggere i dati. Riprova con una foto più nitida.")
                    if data.raw_text:
                         st.caption(f"Dettaglio errore: {data.raw_text}")

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

def _render_management_tab(db, user, all_records, years, def_idx, settings):
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
                _handle_edit_flow(db, user.id, target_rec, settings) # Passa user.id
            elif st.session_state.active_operation == "delete":
                _handle_delete_flow(db, user.id, target_id)

def _handle_edit_flow(db, user_id, rec, settings):
    st.markdown(f"**Modifica Record:** {rec.date}")
    with st.form("fuel_form_edit"):
        min_pe, max_pe = max(0.0, rec.price_per_liter-0.5), rec.price_per_liter+0.5
        
        # Riutilizzo componente UI form
        # NOTA: Qui in edit passiamo il KM reale perché stiamo modificando un dato esistente
        edit_data = forms.render_refueling_inputs(
            rec.date, rec.total_km, rec.price_per_liter, rec.total_cost, 
            rec.is_full_tank, rec.notes, min_pe, max_pe, settings.max_total_cost,
            last_km_known=rec.total_km # In edit il tooltip mostra il km attuale del record
        )
        
        if st.form_submit_button("Aggiorna", type="primary", width="stretch"):
            # Nota: In edit non controlliamo "last_km" stretto come in insert per flessibilità
            new_liters = edit_data['cost'] / edit_data['price'] if edit_data['price'] > 0 else 0
            changes = {
                "date": edit_data['date'], "total_km": edit_data['km'], 
                "price_per_liter": edit_data['price'], "total_cost": edit_data['cost'], 
                "liters": new_liters, "is_full_tank": edit_data['full'], "notes": edit_data['notes']
            }
            crud.update_refueling(db, user_id, rec.id, changes)
            st.success("Record aggiornato!"); st.session_state.active_operation = None; st.rerun()
            
    if st.button("Annulla", width="stretch"):
        st.session_state.active_operation = None; st.rerun()

def _handle_delete_flow(db, user_id, record_id):
    st.error("Sei sicuro di voler eliminare definitivamente questo record?")
    cd1, cd2 = st.columns(2)
    if cd1.button("Sì, Elimina", type="primary", width="stretch"):
        crud.delete_refueling(db, user_id, record_id)
        st.success("Eliminato."); st.session_state.active_operation = None; st.rerun()
    if cd2.button("No, Annulla", width="stretch"):
        st.session_state.active_operation = None; st.rerun()