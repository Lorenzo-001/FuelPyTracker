import streamlit as st
import pandas as pd
from database.core import get_db
from database import crud
from services import importers

def render():
    st.header("⚙️ Gestione Dati e Configurazioni")
    
    tab_config, tab_import, tab_edit = st.tabs(["🔧 Configurazioni", "📥 Import Massivo", "📝 Modifica Storico"])

    with tab_config:
        _render_config_tab()

    with tab_import:
        _render_import_tab()

    with tab_edit:
        _render_edit_tab()

def _render_config_tab():
    """Gestisce i parametri globali dell'app."""
    db = next(get_db())
    settings = crud.get_settings(db)
    
    st.subheader("Parametri Inserimento & Sicurezza")
    st.info("Questi valori definiscono i limiti e gli avvisi dell'applicazione.")
    
    with st.form("config_form"):
        c1, c2 = st.columns(2)
        new_range = c1.number_input(
            "Range Oscillazione Prezzo (€)", 
            min_value=0.01, max_value=0.50, 
            value=settings.price_fluctuation_cents,
            step=0.01,
            help="Quanto può variare il prezzo rispetto all'ultimo inserimento (es. +/- 0.15€)"
        )
        
        new_max = c2.number_input(
            "Tetto Massimo Spesa Pieno (€)", 
            min_value=50.0, max_value=500.0, 
            value=settings.max_total_cost,
            step=10.0,
            help="Importo massimo consentito per un singolo pieno."
        )
        
        st.divider()
        st.markdown("#### 🚨 Soglie di Avviso")
        
        new_alert_threshold = st.number_input(
            "Soglia Allerta Parziali Cumulati (€)",
            min_value=20.0, max_value=500.0,
            value=settings.max_accumulated_partial_cost,
            step=10.0,
            help="Se la somma dei rifornimenti parziali consecutivi supera questo valore, la Dashboard ti suggerirà di fare il pieno."
        )
        
        if st.form_submit_button("Salva Configurazioni"):
            crud.update_settings(db, new_range, new_max, new_alert_threshold)
            st.success("✅ Configurazioni aggiornate!")
    
    db.close()

def _render_import_tab():
    """Gestisce l'upload, la preview (staging) e il salvataggio massivo."""
    uploaded = st.file_uploader("Carica Excel/CSV", type=["csv", "xlsx"])
    
    if uploaded:
        # 1. Parsing in memoria (senza persistenza)
        raw_df = importers.parse_upload_file(uploaded)
        
        st.info("Anteprima dati (Staging Area). Modifica qui se necessario.")
        
        # 2. Editor Interattivo
        edited_df = st.data_editor(raw_df, num_rows="dynamic", use_container_width=True)
        
        if st.button("✅ Conferma e Importa nel DB", type="primary"):
            db = next(get_db())
            bar = st.progress(0)
            try:
                # 3. Loop inserimento
                total = len(edited_df)
                for i, row in edited_df.iterrows():
                    importers.save_single_row(db, row)
                    bar.progress((i + 1) / total)
                
                st.success("Importazione completata!")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Errore import: {e}")
            finally:
                db.close()

def _render_edit_tab():
    """Gestisce la modifica puntuale con Sandwich Validation."""
    db = next(get_db())
    records = crud.get_all_refuelings(db)
    
    # 1. Selezione Record
    options = {f"{r.id} - {r.date} ({r.total_km} Km)": r.id for r in records}
    sel_label = st.selectbox("Seleziona record", list(options.keys()))
    
    if sel_label:
        rec_id = options[sel_label]
        target = next((r for r in records if r.id == rec_id), None)
        
        if target:
            with st.form("edit_form"):
                c1, c2 = st.columns(2)
                new_km = c1.number_input("Nuovi Km", value=target.total_km, step=1)
                new_cost = c2.number_input("Nuovo Costo", value=target.total_cost, step=0.01)
                
                if st.form_submit_button("Aggiorna"):
                    _handle_update(db, rec_id, target.date, new_km, new_cost)
    
    # 2. Undo (Delete Last)
    st.divider()
    last = crud.get_last_refueling(db)
    if last:
        if st.button(f"🗑️ Elimina Ultimo ({last.date})"):
            crud.delete_refueling(db, last.id)
            st.success("Eliminato.")
            st.cache_data.clear()
            st.rerun()
    
    db.close()

def _handle_update(db, rec_id, date_obj, new_km, new_cost):
    """Logica di validazione sandwich e update."""
    neighbors = crud.get_neighbors(db, date_obj)
    
    # Validazione Sandwich
    if neighbors['prev'] and new_km <= neighbors['prev'].total_km:
        st.error(f"⛔ Km devono essere > {neighbors['prev'].total_km} (precedente).")
        return
    if neighbors['next'] and new_km >= neighbors['next'].total_km:
        st.error(f"⛔ Km devono essere < {neighbors['next'].total_km} (successivo).")
        return

    crud.update_refueling(db, rec_id, {"total_km": new_km, "total_cost": new_cost})
    st.success("Aggiornato!")
    st.cache_data.clear()
    st.rerun()