import re

import streamlit as st

from src.database.core import get_db
from src.services.data import exporters
from src.utils.constants import CAR_BRANDS, PLATE_CONFIG

# =============================================================================
# DIALOG GENERAZIONE PDF
# =============================================================================

@st.dialog("Dati Intestazione Documento")
def render(user, year_filter):
    """
    Renderizza il modale per la generazione del Report PDF.
    
    Gestisce due livelli di interattività:
    1. Selettori (Marca, Nazione): Posizionati FUORI dal form per aggiornare la UI in tempo reale.
    2. Input Dati (Targa, Modello): Posizionati DENTRO il form per il submit finale.
    """
    label_year = f"del {year_filter}" if year_filter else "Completo"
    st.markdown(f"Stai generando il registro: **{label_year}**")

    # ------------------------------------------------------------------
    # 1. SELEZIONI INTERATTIVE (Ambito Reactivity)
    # ------------------------------------------------------------------
    # Questi widget devono innescare un rerun immediato per aggiornare le regole di validazione
    
    col_sel_brand, col_sel_country = st.columns(2)
    
    with col_sel_brand:
        # Logica default intelligente
        default_idx = CAR_BRANDS.index("Fiat") if "Fiat" in CAR_BRANDS else 0
        brand_selection = st.selectbox("Seleziona Marca", CAR_BRANDS, index=default_idx)

    with col_sel_country:
        # Selettore Configurazione Targa
        country_options = list(PLATE_CONFIG.keys())
        default_country_idx = country_options.index("Italia") if "Italia" in country_options else 0
        
        selected_country = st.selectbox(
            "Seleziona Nazione Targa", 
            country_options,
            help="Cambia la validazione e la lunghezza massima del campo targa"
        )
        # Recupero configurazione attiva (Regex, Max Len, etc.)
        config = PLATE_CONFIG[selected_country]

    st.divider()

    # ------------------------------------------------------------------
    # 2. FORM DI INPUT DATI (Ambito Transactional)
    # ------------------------------------------------------------------
    with st.form("pdf_form"):
        st.subheader("📝 Dati Documento")
        
        owner = st.text_input("Nome Proprietario", placeholder="Es. Mario Rossi")
        
        c_model_sx, c_model_dx = st.columns(2)
        
        # Logica Marca Custom
        final_brand = brand_selection
        with c_model_sx:
            if brand_selection == "Altro":
                custom_brand = st.text_input("Scrivi la Marca", placeholder="Es. Volvo")
                if custom_brand:
                    final_brand = custom_brand.strip()
            else:
                st.text_input("Marca Selezionata", value=brand_selection, disabled=True)
        
        with c_model_dx:
            model_text = st.text_input("Modello Auto", placeholder="Es. Panda, Golf...")

        full_model_str = f"{final_brand} {model_text}".strip()

        st.write("")
        
        # Input Targa con validazione dinamica
        # Il max_chars viene aggiornato grazie al fatto che 'config' è calcolato fuori dal form
        label_targa = f"Targa ({selected_country})"
        plate_input = st.text_input(
            label_targa, 
            placeholder=f"Es. {config['placeholder']}", 
            max_chars=config['max_len'], 
            help=config['desc']
        ).upper().strip()

        # Validazione Regex (Deferred)
        plate_warning = None
        if plate_input and not re.match(config["regex"], plate_input):
            plate_warning = f"Formato non valido per {selected_country}. Atteso: {config['desc']}"

        st.write("")
        st.markdown("---")
        
        submitted = st.form_submit_button("📄 Genera e Scarica PDF", type="primary", width='stretch')
    
    # ------------------------------------------------------------------
    # 3. GESTIONE SUBMIT E VALIDAZIONE
    # ------------------------------------------------------------------
    if submitted:
        errors = []
        if not owner: errors.append("Il nome del proprietario è obbligatorio.")
        if brand_selection == "Altro" and not custom_brand: errors.append("Hai selezionato 'Altro', specifica la marca.")
        if not model_text: errors.append("Il modello è obbligatorio.")
        if not plate_input: errors.append("La targa è obbligatoria.")
        
        # Visualizzazione Warning Targa (Non bloccante, ma visibile)
        if plate_warning: 
             st.warning(f"⚠️ {plate_warning}")
        
        if errors:
            for e in errors:
                st.error(e)
        else:
            # Trigger Generazione
            _generate_and_download(user, owner, plate_input, full_model_str, year_filter)


def _generate_and_download(user, owner, plate, model, year_filter):
    """
    Orchestra la generazione del PDF e prepara il pulsante di download.
    Separa la gestione della sessione DB dalla UI di Streamlit.
    """
    try:
        with st.spinner("Creazione PDF in corso..."):
            db = next(get_db())
            
            # Chiamata al servizio di export
            pdf_bytes = exporters.generate_maintenance_report(
                db, user.id, owner, plate, model, year_filter
            )
            db.close()
            
            # Costruzione nome file sanitizzato
            year_suffix = f"_{year_filter}" if year_filter else "_FULL"
            safe_plate = re.sub(r'[^A-Z0-9]', '', plate)
            fname = f"ServiceBook_{safe_plate}{year_suffix}.pdf"
            
            st.success("✅ Documento pronto!")
            
            # Rendering bottone download
            st.download_button(
                label="📥 Clicca per Scaricare",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                type="secondary",
                width='stretch'
            )
            
    except Exception as e:
        st.error(f"Errore critico durante la generazione: {e}")