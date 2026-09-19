"""Add-refueling expander: OCR entry + create form."""
import streamlit as st
from datetime import date
from src.database import crud
from src.ui.components.fuel import forms
from src.ui.components.fuel.ocr_dialog import open_ocr_dialog
from src.services.business import fuel_logic
from src.services.ocr.engine import is_openai_enabled
from src.demo import is_demo_mode, writes_disabled


def render_add_panel(db, user, all_records, settings, last_km, last_price, min_p, max_p):
    with st.expander("➕ Registra Nuovo Rifornimento", expanded=False):
        
        # === A. LOGICA SMART SCAN (OCR MODAL) ===
        # Inizializziamo la "bozza" OCR se non esiste
        if "ocr_draft" not in st.session_state:
            st.session_state.ocr_draft = {}

        # Bottone Grande invece di Expander annidato
        st.markdown("##### 📸 Vuoi velocizzare l'inserimento?")
        if writes_disabled():
            st.button("🚀 SCANSIONA SCONTRINO CON AI (Demo)", disabled=True, width='stretch',
                      help="Funzionalità non disponibile in modalità Demo.")
            st.warning("🔒 Modalità Demo: Modifiche disabilitate per sicurezza.")
        elif is_openai_enabled() or is_demo_mode():
            # OpenAI reale, oppure mock OCR in locale/demo
            label = "🚀 SCANSIONA SCONTRINO CON AI (Demo)" if is_demo_mode() and not is_openai_enabled() else "🚀 SCANSIONA SCONTRINO CON AI"
            if st.button(label, type="primary", width='stretch'):
                open_ocr_dialog()
        else:
            st.button("🚀 SCANSIONA SCONTRINO (Non disponibile)", disabled=True, width='stretch', help="Funzionalità disabilitata: API Key OpenAI mancante.")
            st.caption("⚠️ Configura la chiave OpenAI nei settings per abilitare l'AI.")


        # === B. CALCOLO DEFAULTS ===
        # Se abbiamo dati in bozza (da OCR), usiamo quelli. Altrimenti storici.
        draft = st.session_state.ocr_draft
        
        # Priorità: OCR Draft -> Storico/Default
        def_date = draft.get("date", date.today())
        def_price = draft.get("price", last_price)
        def_cost = draft.get("cost", 0.0)
        
        # I KM di default sono None (vuoto) per forzare l'inserimento,
        # ma passiamo last_km come informazione per il tooltip.
        def_km = None 

        st.caption(f"Range suggerito: {min_p:.3f} - {max_p:.3f} €/L")
        
        with st.form("fuel_form_add", clear_on_submit=False):
            # Form delegato al componente UI, passando i defaults dinamici e l'ultimo KM noto per tooltip
            new_data = forms.render_refueling_inputs(
                def_date, def_km, def_price, def_cost, True, "", 
                min_p, max_p, settings.max_total_cost,
                last_km_known=last_km, # Passiamo il dato per il tooltip
                key_suffix="add"
            )
            
            if st.form_submit_button("Salva", type="primary", width="stretch", disabled=writes_disabled(), help="Salvataggio disabilitato in modalità Demo" if writes_disabled() else None):
                # Validazione KM: deve essere > 0 e >= last_km
                if new_data['km'] == 0:
                    st.error("⛔ Inserisci il valore dell'Odometro!")
                else:
                    is_valid, err_msg = fuel_logic.validate_refueling(new_data, all_records)
                    if not is_valid:
                        st.error(err_msg)
                    else:
                        try:
                            liters = new_data['cost'] / new_data['price']
                            crud.create_refueling(db, user.id, new_data['date'], new_data['km'], new_data['price'], 
                                                new_data['cost'], liters, new_data['full'], new_data['notes'])
                            
                            st.success(f"✅ Salvato! ({liters:.2f} L)")
                            
                            # PULIZIA: Reset della bozza OCR dopo salvataggio e pulizia dello stato slider
                            st.session_state.ocr_draft = {}
                            if "price_slider_add" in st.session_state:
                                del st.session_state["price_slider_add"]
                            if "last_default_price_add" in st.session_state:
                                del st.session_state["last_default_price_add"]
                            
                            st.rerun()
                        except Exception as e:
                            st.error(f"Errore DB: {e}")
