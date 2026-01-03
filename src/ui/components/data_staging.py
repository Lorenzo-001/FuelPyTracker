import streamlit as st
import pandas as pd
import time
from src.database.core import get_db
from src.services.data.importers import fuel, maintenance

def render_staging_table(user_id, df, error_msg, data_type):
    """
    Componente UI per visualizzare, editare e salvare i dati di staging.
    
    Args:
        user_id: ID dell'utente corrente.
        df: DataFrame pandas con i dati processati.
        error_msg: Stringa di errore (se presente).
        data_type: 'fuel' oppure 'maintenance'.
    """
    
    # 1. Gestione Errori Bloccanti di lettura file
    if error_msg:
        st.error(f"⚠️ Errore durante la lettura di {data_type}: {error_msg}")
        return

    if df is None or df.empty:
        st.info(f"Nessun dato trovato per {data_type}.")
        return

    # 2. Calcolo Metriche
    n_new = len(df[df['Stato'] == 'Nuovo'])
    n_mod = len(df[df['Stato'] == 'Modifica'])
    n_err = len(df[df['Stato'] == 'Errore'])
    n_tot = len(df)

    # Tooltip helper
    def _get_tooltip(status):
        dates = df[df['Stato'] == status]['Data'].dt.strftime('%d/%m').tolist()[:5]
        return f"Es: {', '.join(dates)}..." if dates else ""

    # 3. Visualizzazione KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Totale Righe", n_tot)
    c2.metric("Nuovi Record", n_new, help=_get_tooltip('Nuovo'))
    c3.metric("Da Aggiornare", n_mod, delta_color="off", help=_get_tooltip('Modifica'))
    c4.metric("Errori", n_err, delta_color="inverse")

    # 4. Configurazione Colonne (Dinamica in base al tipo)
    if data_type == 'fuel':
        cols_cfg = _get_fuel_config()
        validate_func = fuel.validate_fuel_logic
        save_func = fuel.save_row
    else:
        cols_cfg = _get_maintenance_config()
        validate_func = maintenance.validate_maintenance_logic
        save_func = maintenance.save_row

    # 5. Data Editor
    # key univoca basata sul tipo per evitare conflitti tra i due expander
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        width='stretch',
        column_config=cols_cfg,
        key=f"editor_{data_type}",
        height=300
    )

    # 6. Azioni (Bottoni)
    col_actions_1, col_actions_2 = st.columns([1, 3])
    
    with col_actions_1:
        # BOTTONE RIVALIDA
        if st.button(f"🔄 Rivalida", key=f"reval_{data_type}", help="Ricalcola gli stati dopo le tue modifiche"):
            _handle_revalidate(user_id, edited_df, data_type, validate_func)

    with col_actions_2:
        # BOTTONE SALVA
        # Disabilitato se ci sono errori o se non c'è nulla da salvare
        can_save = (n_new + n_mod) > 0 and n_err == 0
        btn_label = f"🚀 Importa {n_new + n_mod} record nel Database"
        
        if st.button(btn_label, key=f"save_{data_type}", type="primary", disabled=not can_save, width='stretch'):
            _handle_save(user_id, edited_df, data_type, save_func)


# --- Helper Methods Interni ---

def _handle_revalidate(user_id, df, data_type, validate_func):
    """Esegue la validazione backend e aggiorna lo stato."""
    db = next(get_db())
    try:
        new_df = validate_func(db, user_id, df)
        # Aggiorna solo la porzione specifica dello stato
        if "import_results" in st.session_state:
            res = st.session_state.import_results
            res[data_type] = (new_df, None)
            st.session_state.import_results = res
        st.rerun()
    finally:
        db.close()

def _handle_save(user_id, df, data_type, save_func):
    """Esegue il salvataggio riga per riga con progress bar."""
    db = next(get_db())
    prog_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        total = len(df)
        success_count = 0
        
        for i, row in df.iterrows():
            # Chiama la funzione di salvataggio specifica (fuel o maint)
            save_func(db, user_id, row)
            
            # Update UI
            prog = (i + 1) / total
            prog_bar.progress(prog)
            status_text.caption(f"Elaborazione riga {i+1}/{total}...")
            time.sleep(0.01) # Piccolo delay per UX fluida
            success_count += 1
            
        st.success(f"✅ Importazione completata! Processati {success_count} record.")
        time.sleep(1)
        
        # Rimuove i dati processati dallo stato per pulire l'interfaccia
        if "import_results" in st.session_state:
            del st.session_state.import_results[data_type]
            # Se non c'è altro, resetta tutto
            if not st.session_state.import_results:
                st.session_state.import_results = {}
        
        st.cache_data.clear() # Invalida cache se usi query cachate altrove
        st.rerun()
        
    except Exception as e:
        st.error(f"Errore critico durante il salvataggio: {e}")
    finally:
        db.close()

def _get_fuel_config():
    return {
        "db_id": None, # Nascosto
        "Stato": st.column_config.TextColumn("Stato", width="small", validate="^(OK|Nuovo|Modifica)$", help="Nuovo, Modifica o Errore"),
        "Note": st.column_config.TextColumn("Log Sistema", width="medium", disabled=True),
        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        "Km": st.column_config.NumberColumn("Km", format="%d"),
        "Prezzo": st.column_config.NumberColumn("€/L", format="%.3f"),
        "Costo": st.column_config.NumberColumn("Totale €", format="%.2f"),
        "Litri": st.column_config.NumberColumn("Litri", disabled=True, format="%.2f"),
        "Pieno": st.column_config.CheckboxColumn("Pieno?"),
        "Note_User": st.column_config.TextColumn("Note Utente")
    }

def _get_maintenance_config():
    return {
        "db_id": None,
        "Stato": st.column_config.TextColumn("Stato", width="small", validate="^(OK|Nuovo|Modifica)$"),
        "Note": st.column_config.TextColumn("Log Sistema", width="medium", disabled=True),
        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        "Km": st.column_config.NumberColumn("Km", format="%d"),
        "Tipo": st.column_config.SelectboxColumn("Tipo Intervento", options=["Tagliando", "Gomme", "Batteria", "Revisione", "Freni", "Altro"], required=True),
        "Costo": st.column_config.NumberColumn("Costo €", format="%.2f"),
        "Descrizione": st.column_config.TextColumn("Dettagli")
    }