import streamlit as st
import pandas as pd
from src.database.core import get_db
from src.database import crud
from src.services import importers

def render():
    st.header("⚙️ Gestione Dati e Configurazioni")
    
    # Recupero utente
    user = st.session_state["user"]

    tab_config, tab_import = st.tabs(["🔧 Configurazioni", "📥 Import Massivo"])

    with tab_config:
        _render_config_tab(user)

    with tab_import:
        _render_import_tab(user)

def _render_config_tab(user):
    """Gestisce i parametri globali dell'app per l'utente specifico."""
    db = next(get_db())
    settings = crud.get_settings(db, user.id)
    
    st.subheader("Parametri Inserimento & Sicurezza")
    
    st.markdown("""
    > **Guida alla Configurazione:**
    > 1. **Range Prezzo:** Limiti dello slider in Rifornimenti.
    > 2. **Tetto Spesa:** Limite massimo di sicurezza.
    > 3. **Soglia Allerta:** Avviso per troppi parziali consecutivi.
    """)
    
    st.write("") 

    with st.form("config_form"):
        st.markdown("##### 🎚️ Limiti Inserimento")
        
        new_range = st.number_input(
            "Range Oscillazione Prezzo (+/- €)", 
            min_value=0.01, max_value=0.50, 
            value=settings.price_fluctuation_cents,
            step=0.01, format="%.2f"
        )
        
        new_max = st.number_input(
            "Tetto Massimo Spesa per Pieno (€)", 
            min_value=50.0, max_value=500.0, 
            value=settings.max_total_cost,
            step=10.0, format="%.2f"
        )
        
        st.divider()
        st.markdown("##### 🚨 Logica Avvisi")
        
        new_alert_threshold = st.number_input(
            "Soglia Allerta Parziali Cumulati (€)",
            min_value=20.0, max_value=500.0,
            value=settings.max_accumulated_partial_cost,
            step=10.0, format="%.2f"
        )
        
        st.write("")
        
        if st.form_submit_button("💾 Salva Configurazioni", type="primary", width="stretch"):
            crud.update_settings(db, user.id, new_range, new_max, new_alert_threshold)
            st.success("✅ Configurazioni aggiornate!")
    
    db.close()

def _render_import_tab(user):
    st.subheader("Caricamento Storico Esterno")

    st.markdown("""
    > **Workflow Importazione Sicura:**
    > 1. **Carica** il file Excel.
    > 2. **Correggi o Elimina** eventuali errori segnalati direttamente nella tabella.
    > 3. Premi **'🔄 Rivalida Dati'** per aggiornare lo stato e rimuovere righe vuote.
    > 4. Quando non ci sono errori bloccanti, il pulsante **Conferma** si attiverà, permettendo l'importazione.
    """)

    uploaded = st.file_uploader("Trascina qui il file", type=["csv", "xlsx"])
    
    # Inizializzazione Stato Sessione
    if "import_df" not in st.session_state:
        st.session_state.import_df = None

    # Logica di Caricamento Iniziale
    if uploaded:
        # Se cambia il file caricato o non c'è ancora un df, processiamo
        # Nota: usiamo un trucco per capire se il file è cambiato -> resettiamo se necessario
        # Per semplicità qui ricarichiamo se 'import_df' è None
        if st.session_state.import_df is None:
            db = next(get_db())
            # Passiamo user.id al parser
            raw_df, error_msg = importers.parse_upload_file(db, user.id, uploaded)
            db.close()
            
            if error_msg:
                st.error(f"❌ Errore fatale: {error_msg}")
            else:
                st.session_state.import_df = raw_df

    # Se c'è un DataFrame in memoria
    if st.session_state.import_df is not None:
        df = st.session_state.import_df
        
        # Conteggio Errori
        n_err = len(df[df['Stato'] == 'Errore'])
        n_warn = len(df[df['Stato'] == 'Warning'])
        
        # Dashboard Stato
        c1, c2, c3 = st.columns(3)
        c1.metric("Righe Totali", len(df))
        c2.metric("Errori Bloccanti", n_err, delta_color="inverse")
        c3.metric("Avvisi", n_warn, delta_color="normal")

        # Pulsante Rivalida
        if st.button("🔄 Rivalida Dati Modificati", type="secondary", width="stretch"):
            db = next(get_db())
            # Passiamo user.id al validatore
            st.session_state.import_df = importers.revalidate_dataframe(db, user.id, st.session_state.import_df)
            db.close()
            st.rerun()

        # Tabella Editabile con DYNAMIC (Permette Delete)
        edited_df = st.data_editor(
            st.session_state.import_df,
            num_rows="dynamic", # Permette di CANCELLARE righe
            width="stretch",
            height=400,
            column_config={
                "Stato": st.column_config.TextColumn(
                    "Stato", 
                    width="small",
                    help="OK = Pronto | Warning = Attenzione | Errore = Bloccante",
                    validate="^(OK|Warning)$"
                ),
                "Note": st.column_config.TextColumn("Problemi Rilevati", width="large", disabled=True),
                "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "Km": st.column_config.NumberColumn("Km", min_value=0, format="%d"),
                "Prezzo": st.column_config.NumberColumn("Prezzo", min_value=0.0, format="%.3f"),
                "Costo": st.column_config.NumberColumn("Costo", min_value=0.0, format="%.2f"),
                "Litri": st.column_config.NumberColumn("Litri (Auto)", disabled=True, format="%.2f")
            },
            key="editor_import_key"
        )
        
        if not edited_df.equals(st.session_state.import_df):
            st.session_state.import_df = edited_df

        st.divider()

        # Pulsante Conferma
        btn_disabled = n_err > 0
        btn_label = f"🚫 Correggi {n_err} errori per proseguire" if btn_disabled else "🚀 Conferma e Scrivi nel Database"
        
        if st.button(btn_label, type="primary", disabled=btn_disabled, use_container_width=True):
            db = next(get_db())
            bar = st.progress(0)
            try:
                count = 0
                total = len(st.session_state.import_df)
                
                for i, row in st.session_state.import_df.iterrows():
                    importers.save_single_row(db, user.id, row)
                    count += 1
                    bar.progress((i + 1) / total)
                
                st.success(f"✅ Importazione completata! Inseriti {count} record.")
                st.session_state.import_df = None # Reset
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Errore critico salvataggio: {e}")
            finally:
                db.close()