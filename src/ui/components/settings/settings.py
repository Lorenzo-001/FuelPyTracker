import streamlit as st
from datetime import datetime
from src.database.core import get_db
from src.database import crud
from src.services.data.exporters import reports, templates
# Importiamo i nuovi moduli refattorizzati
from src.services.data.importers import manager
from src.ui.components.settings import export_dialog, data_staging

@st.fragment
def render():
    st.header("⚙️ Gestione Dati e Configurazioni")
    
    # Recupero utente
    user = st.session_state["user"]

    tab_config, tab_export, tab_import, tab_pdf = st.tabs(["🔧 Configurazioni", "📤 Esportazione Dati", "📥 Importazione Dati", "📄 Libretto Service"])
    
    with tab_config:
        _render_config_tab(user)

    with tab_export:
        _render_export_tab(user)
        
    with tab_import:
        _render_import_tab(user)
        
    with tab_pdf:    
        _render_pdf_tab(user)

def _render_export_tab(user):
    
    st.markdown("""
    In questa sezione puoi scaricare una copia completa dei tuoi dati.
    
    **Cosa contiene il file Excel:**
    * **Foglio 'Rifornimenti':** Tutto lo storico dei pieni, inclusi costi, litri e note.
    * **Foglio 'Manutenzione':** La lista degli interventi effettuati sul veicolo.
    
    **A cosa serve:**
    * 💾 **Backup:** Conserva una copia sicura dei tuoi dati offline.
    * ✏️ **Modifica Massiva:** Puoi modificare questo file e ricaricarlo nella tab "Importazione Dati" per aggiornare velocemente molti record (es. correggere prezzi vecchi).
    """)
    
    st.divider()

    db = next(get_db())
    
    # Calcolo statistiche rapide per l'anteprima
    n_fuels = len(crud.get_all_refuelings(db, user.id))
    n_maints = len(crud.get_all_maintenances(db, user.id))
    
    col1, col2 = st.columns(2)
    col1.metric("Rifornimenti da esportare", n_fuels)
    col2.metric("Interventi da esportare", n_maints)
    
    st.divider()
    
    if st.button("📦 Genera File Excel", type="primary"):
        try:
            # Generazione in RAM
            excel_data = reports.generate_excel_report(db, user.id)
            
            # Nome file con data odierna
            filename = f"fuelpytracker_backup_{datetime.now().strftime('%Y%m%d')}.xlsx"
            
            # Bottone di download effettivo (appare dopo la generazione)
            st.download_button(
                label="📥 Clicca qui per scaricare",
                data=excel_data,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_excel_btn"
            )
            st.success("File generato con successo! Clicca sopra per scaricare.")
            
        except Exception as e:
            st.error(f"Errore durante la generazione: {e}")
    
    db.close()

@st.dialog("Conferma Eliminazione")
def show_delete_dialog(index, label_name):
    st.write(f"Sei sicuro di voler rimuovere la categoria **{label_name}** dalla lista?")
    st.warning("Ricordati di salvare le configurazioni dopo la conferma.")
    
    col1, col2 = st.columns(2)
    if col1.button("Sì, elimina", type="primary", width='stretch'):
        st.session_state.settings_temp_labels.pop(index)
        # Gestione reset indice se stiamo cancellando l'elemento in modifica
        if st.session_state.settings_editing_idx == index:
            st.session_state.settings_editing_idx = -1
        elif st.session_state.settings_editing_idx > index:
            st.session_state.settings_editing_idx -= 1
        st.rerun()
        
    if col2.button("Annulla", width='stretch'):
        st.rerun()

def _render_config_tab(user):
    """Gestisce i parametri globali dell'app per l'utente specifico."""
    db = next(get_db())
    settings = crud.get_settings(db, user.id)
    
    # --- 1. GESTIONE STATO LOCALE (Labels) ---
    if "settings_temp_labels" not in st.session_state:
        st.session_state.settings_temp_labels = settings.reminder_types or [
            "Controllo Livello Olio", "Pressione Pneumatici"
        ]
    
    # Reset indici
    if "settings_editing_idx" not in st.session_state:
        st.session_state.settings_editing_idx = -1

    st.subheader("Parametri Inserimento & Sicurezza")
    
    st.markdown("""
    > **Guida alla Configurazione:**
    > 1. **Range Prezzo:** Imposta la tolleranza dello slider per il prezzo carburante.
    > 2. **Tetto Spesa:** Fissa un limite massimo di sicurezza per evitare errori di digitazione (es. 500€).
    > 3. **Soglia Allerta:** Ricevi un avviso se accumuli troppi rifornimenti parziali consecutivi.
    > 4. **Categorie Promemoria:** Definisci qui le voci che troverai nel menu a tendina "Categoria" quando crei un nuovo promemoria.
    """)
    
    st.write("") 

    with st.form("config_form"):
        # --- SEZIONE 1: Limiti Numerici ---
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
        
        new_alert_threshold = st.number_input(
            "Soglia Allerta Parziali Cumulati (€)",
            min_value=20.0, max_value=500.0,
            value=settings.max_accumulated_partial_cost,
            step=10.0, format="%.2f"
        )
        
        st.divider()
        
        # --- SEZIONE 2: Gestione Categorie Promemoria ---
        st.markdown("##### 🏷️ Gestione Categorie")
        st.caption("Aggiungi o rimuovi le categorie.")

        # A. AREA AGGIUNTA
        c_add_in, c_add_btn = st.columns([5, 1], vertical_alignment="bottom")
        new_label_input = c_add_in.text_input("Nuova Categoria", placeholder="Es. Filtro Abitacolo", label_visibility="collapsed")
        
        # FIX 1: Messaggio se input vuoto
        if c_add_btn.form_submit_button("➕", help="Aggiungi", type="secondary", width='stretch'):
            if new_label_input:
                clean_val = new_label_input.strip()
                if clean_val not in st.session_state.settings_temp_labels:
                    st.session_state.settings_temp_labels.append(clean_val)
                    st.rerun()
                else:
                    st.warning("Categoria già presente nella lista.")
            else:
                st.error("⚠️ Inserisci un nome per la categoria prima di aggiungere.")

        st.write("") 

        # B. LISTA CARD (Mobile Optimized)
        if not st.session_state.settings_temp_labels:
            st.info("Nessuna categoria.")
        
        for i, label in enumerate(st.session_state.settings_temp_labels):
            is_editing = (st.session_state.settings_editing_idx == i)
            
            with st.container(border=True):
                c_text, c_actions_block = st.columns([4, 1.2], vertical_alignment="center")
                
                # --- COLONNA 1: CONTENUTO ---
                with c_text:
                    if is_editing:
                        edit_val = st.text_input(f"ed_{i}", value=label, label_visibility="collapsed")
                    else:
                        st.markdown(f"**{label}**")

                # --- COLONNA 2: PULSANTI ---
                with c_actions_block:
                    b1, b2 = st.columns(2)
                    
                    if is_editing:
                        if b1.form_submit_button("✅", key=f"s_{i}", width='stretch'):
                            if edit_val:
                                st.session_state.settings_temp_labels[i] = edit_val.strip()
                                st.session_state.settings_editing_idx = -1
                                st.rerun()
                        
                        if b2.form_submit_button("❌", key=f"u_{i}", width='stretch'):
                            st.session_state.settings_editing_idx = -1
                            st.rerun()
                    else:
                        if b1.form_submit_button("✏️", key=f"e_{i}", help="Modifica", width='stretch'):
                            st.session_state.settings_editing_idx = i
                            st.rerun()
                            
                        # FIX 2: Apertura Dialog conferma eliminazione
                        if b2.form_submit_button("❌", key=f"d_{i}", help="Elimina", width='stretch'):
                            show_delete_dialog(i, label)

        st.write("")
        st.write("")
        
        # --- SALVATAGGIO FINALE ---
        if st.form_submit_button("💾 Salva Configurazioni", type="primary", width='stretch'):
            crud.update_settings(
                db, user.id, 
                new_range, 
                new_max, 
                new_alert_threshold,
                st.session_state.settings_temp_labels
            )
            del st.session_state["settings_temp_labels"]
            del st.session_state["settings_editing_idx"]
            
            st.success("✅ Configurazioni salvate con successo!")
            st.rerun()
    
    db.close()

def _render_import_tab(user):
    st.subheader("Caricamento Dati (Multi-Scheda)")

    st.markdown("""
    > **Workflow Importazione Sicura:**
    > 1. **Scarica il Modello** (opzionale) o usa un tuo file Excel.
    > 2. **Carica** il file qui sotto.
    > 3. **Correggi** eventuali errori segnalati nella tabella di anteprima.
    > 4. Premi **Conferma** per salvare i dati nel database.
    """)

    # --- Expander Guida + Download ---
    with st.expander("❓ Non hai un file? Scarica il modello e leggi la guida"):
        
        st.markdown("##### 1. Istruzioni Compilazione")
        st.info("""
        * **Rifornimenti:** Compila il foglio 'Rifornimenti' e/o il foglio 'Manutenzione'.
        * **Date:** Usa il formato `GG/MM/AAAA` (es. 25/12/2023).
        * **Numeri:** Usa il punto o la virgola per i decimali (es. 1.859 o 1,859).
        * **Pieno:** Scrivi `Sì` se hai fatto il pieno.
        * **Importante:** Non modificare i nomi delle colonne della prima riga.
        """)
    
        st.markdown("##### 2. Scarica Template")
        st.write("File Excel vuoto con le intestazioni corrette.")
        empty_template = templates.generate_empty_template()
        st.download_button(
            label="📥 Scarica Modello .xlsx",
            data=empty_template,
            file_name="FuelPyTracker_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )

    # --- GESTIONE RESET UPLOADER ---
    # Usiamo un contatore nella sessione per creare una chiave dinamica.
    # Quando incrementiamo il contatore, Streamlit resetta il widget file_uploader.
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0

    uploaded = st.file_uploader(
        "Trascina qui il file (CSV o Excel)", 
        type=["csv", "xlsx"],
        key=f"uploader_{st.session_state['uploader_key']}" # Chiave dinamica
    )
    
    # Stato per i risultati multipli
    if "import_results" not in st.session_state:
        st.session_state.import_results = {}

    if uploaded:
        # Se i risultati sono vuoti (primo caricamento), processiamo usando il nuovo Manager
        if not st.session_state.import_results:
            db = next(get_db())
            # USIAMO IL NUOVO MANAGER
            results = manager.parse_upload_file(db, user.id, uploaded)
            db.close()
            
            # Check errore globale (es. file corrotto o nessun foglio valido)
            if 'global_error' in results:
                st.error(f"❌ {results['global_error']}")
            else:
                st.session_state.import_results = results
    else:
        # Reset implicito (se clicchi la X del widget)
        st.session_state.import_results = {}

    # --- RENDER RISULTATI (Dinamico tramite componente esterno) ---
    results = st.session_state.import_results
    
    if results:
        # 1. Sezione Rifornimenti
        if 'fuel' in results:
            with st.expander("⛽ Rifornimenti Trovati", expanded=True):
                df_fuel, err_fuel = results['fuel']
                data_staging.render_staging_table(user.id, df_fuel, err_fuel, "fuel")

        # 2. Sezione Manutenzione
        if 'maintenance' in results:
            with st.expander("🔧 Manutenzioni Trovate", expanded=True):
                df_maint, err_maint = results['maintenance']
                data_staging.render_staging_table(user.id, df_maint, err_maint, "maintenance")
        
        st.divider()
        
        # --- PULSANTE RESET LOGICA ---
        if st.button("🔄 Pulisci tutto e carica altro file", type="secondary"):
            # 1. Puliamo i risultati
            st.session_state.import_results = {}
            # 2. Incrementiamo la chiave per forzare la distruzione del widget uploader
            st.session_state["uploader_key"] += 1
            # 3. Ricarichiamo la pagina
            st.rerun()

def _render_pdf_tab(user):
    st.subheader("Libretto Manutenzione Digitale")
    
    st.info(
        "Genera un documento PDF ufficiale con lo storico delle manutenzioni. "
        "Puoi scegliere se generare l'intero storico o solo un anno specifico."
    )
    
    # 1. Recupero Anni Disponibili dal DB
    db = next(get_db())
    all_maints = crud.get_all_maintenances(db, user.id)
    db.close()
    
    available_years = sorted(list(set(m.date.year for m in all_maints)), reverse=True)
    
    # Se non ci sono dati, aggiungiamo l'anno corrente come fallback
    if not available_years:
        available_years = [datetime.now().year]

    st.divider()

    # 2. Layout Controlli (Filtro + Bottone)
    c1, c2 = st.columns([1, 2])
    
    with c1:
        # Selectbox con opzione "Tutti" e anni disponibili
        options = ["Tutti gli anni"] + available_years
        selected_option = st.selectbox("Seleziona Periodo", options)
        
        # Determiniamo il valore da passare (None o int)
        year_filter = None if selected_option == "Tutti gli anni" else selected_option

    with c2:
        st.write("") # Spacer per allineare il bottone in basso
        st.write("") 
        
        # Il bottone ora apre il Dialog gestito dal nuovo componente
        if st.button("🖨️ Configura e Genera PDF", type="primary"):
            export_dialog.render(user, year_filter)