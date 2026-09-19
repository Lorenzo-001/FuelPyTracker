import streamlit as st
from src.database.core import get_db
from src.database import crud
from . import export_dialog


def render(user):
    st.subheader("Libretto Manutenzione Digitale")
    
    st.info(
        "Genera un documento PDF ufficiale con lo storico delle manutenzioni. "
        "Puoi scegliere se generare l'intero storico o solo un anno specifico."
    )
    
    # 1. Recupero Anni Disponibili dal DB
    db = next(get_db())
    all_maints = crud.get_all_maintenances(db, user.id)
    db.close()
    
    # Guard: nessuna manutenzione registrata
    if not all_maints:
        st.warning("ℹ️ Nessuna manutenzione registrata. Aggiungi degli interventi prima di generare il PDF.")
        return
    
    available_years = sorted(list(set(m.date.year for m in all_maints)), reverse=True)

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
