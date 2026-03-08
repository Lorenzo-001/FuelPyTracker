import time

import pandas as pd
import streamlit as st

from src.database.core import get_db
from src.services.data.importers import fuel, maintenance
from src.demo import is_demo_mode

# =============================================================================
# COMPONENTE DI STAGING (REVIEW IMPORT)
# =============================================================================

def render_staging_table(user_id: str, df: pd.DataFrame, error_msg: str, data_type: str):
    """
    Componente UI principale per la revisione dei dati prima dell'importazione nel DB.
    Gestisce la visualizzazione, l'editing in linea e il commit dei dati.

    Args:
        user_id (str): ID utente corrente.
        df (pd.DataFrame): DataFrame contenente i dati parsati.
        error_msg (str): Eventuale errore bloccante dal parser.
        data_type (str): Tipo dati ('fuel' | 'maintenance').
    """
    
    # 1. Gestione Errori Preliminari
    if error_msg:
        st.error(f"⚠️ Errore durante la lettura: {error_msg}")
        return

    if df is None or df.empty:
        st.info(f"Nessun dato trovato per la categoria {data_type}.")
        return

    # 2. Calcolo KPI e Metriche
    # Fornisce un riassunto immediato dello stato del file importato
    n_new  = len(df[df['Stato'] == 'Nuovo'])
    n_mod  = len(df[df['Stato'] == 'Modifica'])
    n_warn = len(df[df['Stato'] == 'Warning'])
    n_err  = len(df[df['Stato'] == 'Errore'])
    n_tot  = len(df)

    def _get_tooltip(status):
        """Helper per mostrare anteprima date nel tooltip"""
        dates = df[df['Stato'] == status]['Data'].dt.strftime('%d/%m').tolist()[:5]
        return f"Es: {', '.join(dates)}..." if dates else ""

    # Visualizzazione KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Totale Righe", n_tot)
    c2.metric("Nuovi Record", n_new, help=_get_tooltip('Nuovo'))
    c3.metric("Da Aggiornare", n_mod, delta_color="off", help=_get_tooltip('Modifica'))
    c4.metric("Errori", n_err, delta_color="inverse")
    if n_warn:
        st.warning(f"⚠️ {n_warn} riga/e con anomalie rilevate (Warning): verranno importate ma meritano un controllo manuale.", icon="⚠️")

    # 3. Configurazione Dinamica Colonne
    # Seleziona la configurazione e le funzioni di callback in base al tipo dati
    if data_type == 'fuel':
        cols_cfg = _get_fuel_config()
        validate_func = fuel.validate_fuel_logic
        save_func = fuel.save_row
    else:
        cols_cfg = _get_maintenance_config()
        validate_func = maintenance.validate_maintenance_logic
        save_func = maintenance.save_row

    # 4. Rendering Data Editor
    # Utilizziamo una key univoca per evitare conflitti di stato tra i tab
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        width='stretch',
        column_config=cols_cfg,
        key=f"editor_{data_type}",
        height=300
    )

    # 5. Barra delle Azioni
    col_actions_1, col_actions_2 = st.columns([1, 3])
    
    with col_actions_1:
        # Action: RIVALIDA
        # Utile se l'utente corregge manualmente dei dati nell'editor e vuole ricalcolare lo stato
        if st.button(f"🔄 Rivalida", key=f"reval_{data_type}", help="Ricalcola gli stati dopo le tue modifiche", disabled=is_demo_mode()):
            _handle_revalidate(user_id, edited_df, data_type, validate_func)

    with col_actions_2:
        # Action: COMMIT (SALVA)
        # Abilitato solo se ci sono dati validi (Nuovo/Modifica/Warning), zero errori bloccanti e non in corso un salvataggio
        is_saving = st.session_state.get(f'import_saving_{data_type}', False)
        n_saveable = n_new + n_mod + n_warn
        can_save = n_saveable > 0 and n_err == 0 and not is_saving
        btn_label = (
            f"⏳ Importazione in corso..." if is_saving
            else f"🚀 Importa {n_saveable} record nel Database"
        )

        if st.button(btn_label, key=f"save_{data_type}", type="primary",
                     disabled=(not can_save) or is_demo_mode(), width='stretch'):
            st.session_state[f'import_saving_{data_type}'] = True
            _handle_save(user_id, edited_df, data_type, save_func)


# =============================================================================
# LOGICA DI CONTROLLO & SALVATAGGIO
# =============================================================================

def _handle_revalidate(user_id, df, data_type, validate_func):
    """
    Esegue la logica di validazione backend sul DataFrame modificato dalla UI.
    Aggiorna lo stato di sessione e forza un rerun.
    """
    db = next(get_db())
    try:
        new_df = validate_func(db, user_id, df)
        
        # Aggiornamento puntuale dello stato di sessione
        if "import_results" in st.session_state:
            res = st.session_state.import_results
            res[data_type] = (new_df, None)
            st.session_state.import_results = res
        
        st.rerun()
    finally:
        db.close()


def _handle_save(user_id, df, data_type, save_func):
    """
    Itera sulle righe del DataFrame ed esegue il salvataggio atomico per riga.
    Fornisce feedback visivo tramite Progress Bar.
    Al termine mostra un toast di riepilogo e chiude il componente di staging.
    """
    db = next(get_db())
    prog_bar = st.progress(0)
    status_text = st.empty()

    try:
        total = len(df)
        success_count = 0

        # Loop di persistenza con enumerate per progress bar corretta
        for i, (_, row) in enumerate(df.iterrows()):
            save_func(db, user_id, row)

            prog = (i + 1) / total
            prog_bar.progress(prog)
            status_text.caption(f"Elaborazione riga {i + 1}/{total}...")
            time.sleep(0.01)
            success_count += 1

        # Rimozione dati processati dallo staging area (chiude il componente)
        if "import_results" in st.session_state:
            del st.session_state.import_results[data_type]
            if not st.session_state.import_results:
                st.session_state.import_results = {}

        # Invalidazione cache per riflettere i nuovi dati nelle dashboard
        st.cache_data.clear()

        # Toast di conferma (persiste dopo il rerun, visibile ~4 secondi)
        label_map = {'fuel': 'Rifornimenti', 'maintenance': 'Manutenzioni'}
        section = label_map.get(data_type, data_type)
        st.toast(
            f"✅ {success_count} record di {section} importati con successo!",
            icon="⛽" if data_type == 'fuel' else "🔧"
        )

    except Exception as e:
        st.error(f"Errore critico durante il salvataggio: {e}")
    finally:
        # Sempre: rimuovi il flag anti-click e forza chiusura del componente
        st.session_state.pop(f'import_saving_{data_type}', None)
        db.close()
        st.rerun()


# =============================================================================
# CONFIGURAZIONI COLONNE (Streamlit Column Config)
# =============================================================================

def _get_fuel_config():
    """Configurazione visuale per la tabella Rifornimenti."""
    return {
        "db_id": None,  # Colonna tecnica nascosta
        "Stato": st.column_config.TextColumn(
            "Stato", width="small",
            validate="^(OK|Nuovo|Modifica|Invariato|Warning|Errore)$",
            help="Nuovo, Modifica, Invariato, Warning o Errore"
        ),
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
    """Configurazione visuale per la tabella Manutenzione."""
    return {
        "db_id": None,
        "Stato": st.column_config.TextColumn(
            "Stato", width="small",
            validate="^(OK|Nuovo|Modifica|Invariato|Warning|Errore)$"
        ),
        "Note": st.column_config.TextColumn("Log Sistema", width="medium", disabled=True),
        "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
        "Km": st.column_config.NumberColumn("Km", format="%d"),
        "Tipo": st.column_config.SelectboxColumn(
            "Tipo Intervento", 
            options=["Tagliando", "Gomme", "Batteria", "Revisione", "Freni", "Altro"], 
            required=True
        ),
        "Costo": st.column_config.NumberColumn("Costo €", format="%.2f"),
        "Descrizione": st.column_config.TextColumn("Dettagli")
    }