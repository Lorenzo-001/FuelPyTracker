import streamlit as st
import re
from src.utils.constants import CAR_BRANDS, PLATE_CONFIG
from src.services.data import exporters
from src.database.core import get_db

@st.dialog("Dati Intestazione Documento")
def render(user, year_filter):
    """
    Renderizza il dialog per la generazione del PDF.
    I selettori che modificano il layout (Marca e Nazione) sono FUORI dal form
    per permettere l'aggiornamento dinamico dell'interfaccia.
    """
    label_year = f"del {year_filter}" if year_filter else "Completo"
    st.markdown(f"Stai generando il registro: **{label_year}**")

    # ------------------------------------------------------------------
    # 1. SELEZIONI INTERATTIVE (FUORI DAL FORM)
    # ------------------------------------------------------------------
    # Devono stare fuori per aggiornare la pagina appena le cambi
    
    col_sel_brand, col_sel_country = st.columns(2)
    
    with col_sel_brand:
        # Selettore Marca
        default_idx = CAR_BRANDS.index("Fiat") if "Fiat" in CAR_BRANDS else 0
        brand_selection = st.selectbox(
            "Seleziona Marca", 
            CAR_BRANDS, 
            index=default_idx
        )

    with col_sel_country:
        # Selettore Nazione
        country_options = list(PLATE_CONFIG.keys())
        default_country_idx = country_options.index("Italia") if "Italia" in country_options else 0
        selected_country = st.selectbox(
            "Seleziona Nazione Targa", 
            country_options,
            help="Cambia la validazione e la lunghezza massima del campo targa"
        )
        # Recuperiamo subito la configurazione aggiornata
        config = PLATE_CONFIG[selected_country]

    st.divider()

    # ------------------------------------------------------------------
    # 2. FORM DI INSERIMENTO DATI
    # ------------------------------------------------------------------
    with st.form("pdf_form"):
        st.subheader("📝 Dati Documento")
        
        # Nome Proprietario
        owner = st.text_input("Nome Proprietario", placeholder="Es. Mario Rossi")
        
        c_model_sx, c_model_dx = st.columns(2)
        
        # --- LOGICA MARCA DINAMICA ---
        # Usiamo i dati selezionati sopra (fuori dal form)
        final_brand = brand_selection
        
        with c_model_sx:
            if brand_selection == "Altro":
                # Questo campo appare solo se sopra è selezionato "Altro"
                custom_brand = st.text_input("Scrivi la Marca", placeholder="Es. Volvo")
                if custom_brand:
                    final_brand = custom_brand.strip()
            else:
                # Mostriamo solo un testo disabilitato per conferma visiva
                st.text_input("Marca Selezionata", value=brand_selection, disabled=True)
        
        with c_model_dx:
            model_text = st.text_input("Modello Auto", placeholder="Es. Panda, Golf...")

        # Combinazione stringa finale
        full_model_str = f"{final_brand} {model_text}".strip()

        st.write("")
        
        # --- LOGICA TARGA DINAMICA ---
        # Qui il max_chars si aggiorna perché 'config' è stato ricalcolato fuori dal form
        label_targa = f"Targa ({selected_country})"
        
        plate_input = st.text_input(
            label_targa, 
            placeholder=f"Es. {config['placeholder']}", 
            max_chars=config['max_len'], # <--- Ora questo si aggiorna subito!
            help=config['desc']
        ).upper().strip()

        # Validazione visiva (dentro il form non è realtime carattere per carattere, 
        # ma l'avviso apparirà al submit. Se vuoi realtime totale, anche questo va fuori form)
        plate_warning = None
        if plate_input and not re.match(config["regex"], plate_input):
            plate_warning = f"Formato non valido per {selected_country}. Atteso: {config['desc']}"

        st.write("")
        st.markdown("---")
        
        # Bottone di invio
        submitted = st.form_submit_button("📄 Genera e Scarica PDF", type="primary", use_container_width=True)
    
    # ------------------------------------------------------------------
    # 3. GESTIONE SUBMIT
    # ------------------------------------------------------------------
    if submitted:
        errors = []
        if not owner: errors.append("Il nome del proprietario è obbligatorio.")
        if brand_selection == "Altro" and not custom_brand: errors.append("Hai selezionato 'Altro', specifica la marca.")
        if not model_text: errors.append("Il modello è obbligatorio.")
        if not plate_input: errors.append("La targa è obbligatoria.")
        
        # Mostriamo il warning targa come errore bloccante o avviso
        if plate_warning: 
             st.warning(f"⚠️ {plate_warning}")
             # Se vuoi bloccare, aggiungi a errors: errors.append(plate_warning)
        
        if errors:
            for e in errors:
                st.error(e)
        else:
            # Procedi solo se non ci sono errori bloccanti
            _generate_and_download(user, owner, plate_input, full_model_str, year_filter)


def _generate_and_download(user, owner, plate, model, year_filter):
    try:
        # Spinner fuori dal form per estetica migliore
        with st.spinner("Creazione PDF in corso..."):
            db = next(get_db())
            
            pdf_bytes = exporters.generate_maintenance_report(
                db, user.id, owner, plate, model, year_filter
            )
            db.close()
            
            year_suffix = f"_{year_filter}" if year_filter else "_FULL"
            safe_plate = re.sub(r'[^A-Z0-9]', '', plate)
            fname = f"ServiceBook_{safe_plate}{year_suffix}.pdf"
            
            st.success("✅ Documento pronto!")
            st.download_button(
                label="📥 Clicca per Scaricare",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                type="secondary",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Errore generazione: {e}")