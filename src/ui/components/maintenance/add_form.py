import streamlit as st
from datetime import date
from src.database import crud
from src.ui.components.maintenance import dialogs, forms

def render_add_form(db, user):
    """Renderizza il form di inserimento nuovo record."""
    with st.container(border=True):
        st.markdown("##### ✨ Nuovo Intervento")
        with st.form("new_maint_form", clear_on_submit=False): 
            last_km = crud.get_max_km(db, user.id)
            data = forms.render_maintenance_inputs(date.today(), last_km, "Tagliando", 0.0, "")
            
            if st.form_submit_button("Salva Intervento", type="primary", width="stretch"):
                # Validazioni Base
                if data['cost'] < 0:
                    st.error("Inserire un costo valido.")
                    return
                if data['expiry_km'] and data['expiry_km'] <= data['km']:
                    st.error(f"⚠️ Errore Logico: La scadenza ({data['expiry_km']} km) deve essere maggiore dei km attuali.")
                    return
                if data['expiry_date'] and data['expiry_date'] <= data['date']:
                    st.error("⚠️ Errore Logico: La data di scadenza deve essere successiva alla data dell'intervento.")
                    return

                # Duplicate Check
                if data['expiry_km'] or data['expiry_date']:
                    existing_deadline = crud.get_future_maintenance_by_type(db, user.id, data['type'])
                    if existing_deadline:
                        dialogs.render_conflict_dialog(db, user, data, existing_deadline)
                        return

                # Salvataggio Diretto
                dialogs.perform_save(db, user.id, data)