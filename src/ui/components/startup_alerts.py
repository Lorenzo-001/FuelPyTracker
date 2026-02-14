import streamlit as st
from datetime import date
from src.database import crud
from src.database.core import get_db

@st.dialog("⚠️ Avvisi Veicolo")
def _show_alert_dialog(overdue_list):
    st.write(f"Ci sono **{len(overdue_list)}** attività che richiedono la tua attenzione:")
    
    for item in overdue_list:
        st.error(item, icon="🚨")
        
    st.write("")
    if st.button("Ho capito, vado ai Promemoria", type="primary", width='stretch'):
        st.session_state.current_page = "Manutenzione" # O la pagina dove sono i reminder
        st.rerun()

def check_and_show_alerts(user_id):
    """
    Da chiamare all'inizio di main.py o della dashboard.
    Esegue il controllo solo una volta per sessione.
    """
    if "startup_alert_shown" in st.session_state:
        return

    db = next(get_db())
    
    # 1. Recupero Dati per Check
    # (Logica semplificata: controlliamo solo i Reminder per ora, estendibile a scadenze bollo/rev)
    refuelings = crud.get_all_refuelings(db, user_id)
    current_km = max(r.total_km for r in refuelings) if refuelings else 0
    active_rems = crud.get_active_reminders(db, user_id)
    today = date.today()
    
    overdue_msgs = []
    
    for rem in active_rems:
        # Check Km
        if rem.frequency_km and (current_km - rem.last_km_check) >= rem.frequency_km:
            diff = current_km - (rem.last_km_check + rem.frequency_km)
            overdue_msgs.append(f"**{rem.title}**: Scaduto da {diff} km")
            
        # Check Giorni
        elif rem.frequency_days:
            days_passed = (today - rem.last_date_check).days
            if days_passed >= rem.frequency_days:
                diff = days_passed - rem.frequency_days
                overdue_msgs.append(f"**{rem.title}**: Scaduto da {diff} giorni")

    db.close()

    # 2. Mostra Dialog se necessario
    if overdue_msgs:
        _show_alert_dialog(overdue_msgs)
        
    # 3. Segna come visto
    st.session_state.startup_alert_shown = True