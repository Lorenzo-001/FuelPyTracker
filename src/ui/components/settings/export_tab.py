import streamlit as st
from datetime import datetime
from src.database.core import get_db
from src.database import crud
from src.services.data.exporters import reports


def render(user):
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
    
    if n_fuels == 0 and n_maints == 0:
        st.info("ℹ️ Nessun dato da esportare. Aggiungi prima dei rifornimenti o delle manutenzioni.")
    elif st.button("📦 Genera File Excel", type="primary",
                   disabled=(n_fuels == 0),
                   help="Aggiungi almeno un rifornimento per abilitare l'esportazione." if n_fuels == 0 else None):
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
