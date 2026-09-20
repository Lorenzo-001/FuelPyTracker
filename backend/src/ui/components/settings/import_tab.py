import streamlit as st
from src.database.core import get_db
from src.services.data.exporters import templates
from src.services.data.importers import manager
from . import data_staging
from src.demo import writes_disabled


def render(user):
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
    if writes_disabled():
        st.warning("🔒 Modalità Demo: Modifiche disabilitate per sicurezza.")
        return

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
