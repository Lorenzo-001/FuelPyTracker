import streamlit as st
import pandas as pd
from datetime import date
from src.database.core import get_db
from src.database import crud
from src.ui.components.fuel import grids, kpi, forms
from src.services.business import fuel_logic
from src.services.ocr import process_receipt_image
from src.services.ocr.engine import is_openai_enabled
from src.demo import is_demo_mode

@st.fragment
def render():
    """Vista Principale: Gestione Rifornimenti (Refactored)."""
    st.header("⛽ Gestione Rifornimenti")
    
    # --- 1. Init Stato & DB ---
    # Get utente (Salvato in main.py dopo il login)
    user = st.session_state["user"]

    if "active_operation" not in st.session_state:
        st.session_state.active_operation = None
    if "selected_record_id" not in st.session_state:
        st.session_state.selected_record_id = None

    db = next(get_db())
    all_records = crud.get_all_refuelings(db, user.id)
    last_record = crud.get_last_refueling(db, user.id)
    settings = crud.get_settings(db, user.id)
    
    # Setup Defaults
    last_km = last_record.total_km if last_record else 0
    last_price = last_record.price_per_liter if last_record else 1.650
    years = sorted(list(set(r.date.year for r in all_records)), reverse=True)
    if not years: years = [date.today().year]

    # --- 2. Top Bar & KPI ---
    # Determina indice default in modo sicuro
    def_idx = years.index(date.today().year) if date.today().year in years else 0
    view_year = st.selectbox("📅 Visualizza Anno", years, index=def_idx, key="view_year_sel")
    
    # Calcolo KPI (Delegato al service logic)
    stats = fuel_logic.calculate_year_kpis(all_records, view_year)
    
    kpi.render_fuel_cards(
        view_year, stats["total_cost"], stats["total_liters"], 
        stats["km_est"], stats["avg_price"], stats["min_eff"], stats["max_eff"]
    )

    # --- 3. Area Inserimento (ADD) ---
    range_val = settings.price_fluctuation_cents
    min_p, max_p = max(0.0, last_price - range_val), last_price + range_val

    with st.expander("➕ Registra Nuovo Rifornimento", expanded=False):
        
        # === A. LOGICA SMART SCAN (OCR MODAL) ===
        # Inizializziamo la "bozza" OCR se non esiste
        if "ocr_draft" not in st.session_state:
            st.session_state.ocr_draft = {}

        # Bottone Grande invece di Expander annidato
        st.markdown("##### 📸 Vuoi velocizzare l'inserimento?")
        if is_demo_mode():
            # DEMO MODE: OCR disabilitato — la modalità demo non consente upload reali
            st.button("🚀 SCANSIONA SCONTRINO CON AI (Demo)", disabled=True, width='stretch',
                      help="Funzionalità non disponibile in modalità Demo.")
            st.warning("🔒 Modalità Demo: Modifiche disabilitate per sicurezza.")
        elif is_openai_enabled():
            # CASO POSITIVO: Mostra il bottone normale
            if st.button("🚀 SCANSIONA SCONTRINO CON AI", type="primary", width='stretch'):
                _open_ocr_dialog()
        else:
            # CASO NEGATIVO: Mostra bottone disabilitato o avviso
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
                last_km_known=last_km # Passiamo il dato per il tooltip
            )
            
            if st.form_submit_button("Salva", type="primary", width="stretch"):
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
                            
                            # PULIZIA: Reset della bozza OCR dopo salvataggio
                            st.session_state.ocr_draft = {}
                            
                            st.rerun()
                        except Exception as e:
                            st.error(f"Errore DB: {e}")

    st.write("") 

    # --- 4. Tabs: Storico & Gestione ---
    tab_list, tab_manage = st.tabs(["📋 Storico", "🛠️ Gestione"])

    # TAB A: Lista
    with tab_list:
        _render_history_tab(stats["view_records"], view_year)

    # TAB B: Modifica/Elimina
    with tab_manage:
        _render_management_tab(db, user, all_records, years, def_idx, settings)
    
    db.close()

# --- Helper Functions Locali (per pulizia render principale) ---

@st.dialog("📸 Scansione Smart Scontrino")
def _open_ocr_dialog():
    """
    Gestisce l'UI per lo Smart Scan all'interno di un MODAL POP-UP.
    Usa un file_uploader unificato: su mobile mostra "Scatta Foto" dal menu nativo,
    su desktop apre il selettore file del sistema operativo.
    """

    # Istruzioni contestuali (mobile vs desktop)
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(99,110,250,0.15), rgba(0,204,150,0.10));
            border: 1px solid rgba(99,110,250,0.35);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
            line-height: 1.6;
        ">
            <span style="font-size:1.05em;">📱 <strong>Su mobile:</strong> tocca il pulsante e scegli <em>"Scatta Foto"</em> per usare la fotocamera</span><br>
            <span style="font-size:1.05em;">🖥️ <strong>Su desktop:</strong> seleziona un file immagine (JPG, PNG) dal tuo computer</span><br>
            <span style="font-size:0.85em; opacity:0.75;">💡 Assicurati che la foto sia <strong>ben illuminata</strong> e <strong>a fuoco</strong> per risultati migliori.</span>
        </div>
    """, unsafe_allow_html=True)

    img_buffer = st.file_uploader(
        "Carica o scatta la foto dello scontrino",
        type=['png', 'jpg', 'jpeg'],
        key="ocr_upl",
        label_visibility="collapsed",
        help="Su mobile: scegli 'Scatta Foto' per aprire la fotocamera nativa"
    )

    if img_buffer:
        # Anteprima immagine caricata
        st.image(img_buffer, caption="📄 Anteprima scontrino", width='stretch')
        st.divider()
        if st.button("✨ Analizza con AI", type="primary", width='stretch'):
            with st.spinner("Analisi AI in corso..."):
                # Chiamata al servizio
                data = process_receipt_image(img_buffer)
                
                if data.total_cost > 0:
                    # Salviamo i risultati nello stato per precompilare il form
                    st.session_state.ocr_draft = {
                        "date": data.date if data.date else date.today(),
                        "price": data.price_per_liter,
                        "cost": data.total_cost
                    }
                    st.success("✅ Dati estratti con successo! Il form è stato precompilato.")
                    st.rerun()  # Chiude il modale e aggiorna la pagina sotto
                else:
                    _show_ocr_error(data.raw_text)


def _show_ocr_error(raw_text: str):
    """
    Interpreta il raw_text del backend OCR e mostra un messaggio d'errore
    specifico con causa e azione consigliata, invece di un generico st.error.
    """
    rt = raw_text or ""

    if "API Key" in rt and ("mancante" in rt or "secrets" in rt.lower()):
        # Chiave OpenAI non configurata nell'ambiente
        st.error("⚙️ **Funzionalità non configurata**")
        st.info(
            "La chiave API di OpenAI non è presente nella configurazione dell'app.\n\n"
            "**Come risolvere:** Aggiungi la variabile `openai.api_key` nel file "
            "`.streamlit/secrets.toml` (locale) o nei Secrets di Streamlit Cloud."
        )

    elif "ERRORE AUTH" in rt or "non è valida" in rt or "scaduta" in rt:
        # Chiave configurata ma non valida o scaduta
        st.error("🔑 **API Key OpenAI non valida o scaduta**")
        st.info(
            "La chiave API di OpenAI è rifiutata dai server. Potrebbe essere:\n"
            "- Scaduta o revocata\n"
            "- Troncata durante la configurazione\n\n"
            "**Come risolvere:** Vai su [platform.openai.com](https://platform.openai.com/api-keys) "
            "e rigenera la chiave, poi aggiornala nei Secrets."
        )

    elif "ERRORE QUOTA" in rt or "Credito" in rt or "limite richieste" in rt:
        # Credito OpenAI esaurito o rate limit
        st.error("💸 **Credito OpenAI esaurito o limite raggiunto**")
        st.info(
            "Il tuo account OpenAI ha esaurito il credito disponibile o hai raggiunto "
            "il limite di richieste per questo periodo.\n\n"
            "**Come risolvere:** Verifica il tuo saldo e i limiti su "
            "[platform.openai.com/usage](https://platform.openai.com/usage)."
        )

    elif "ERRORE RETE" in rt or "Impossibile connettersi" in rt:
        # Problemi di connessione a Internet / OpenAI
        st.error("🌐 **Errore di connessione di rete**")
        st.info(
            "Impossibile raggiungere i server OpenAI.\n\n"
            "**Come risolvere:** Controlla la connessione internet e riprova tra qualche secondo."
        )

    elif "ERRORE AI" in rt or "formato non valido" in rt or "JSONDecodeError" in rt:
        # L'AI ha risposto correttamente ma con formato non parsabile
        st.error("🤖 **L'AI non ha riconosciuto lo scontrino**")
        st.info(
            "L'intelligenza artificiale non è riuscita a identificare i dati chiave "
            "(costo totale, prezzo al litro) nell'immagine.\n\n"
            "**Suggerimenti per una scansione migliore:**\n"
            "- Assicurati che la foto sia **a fuoco** e ben illuminata\n"
            "- Inquadra solo lo scontrino, evita ombre o riflessi\n"
            "- Ritenta la scansione o inserisci i dati manualmente"
        )

    else:
        # ➜ Fallback generico per errori imprevisti
        st.error("❌ **Errore durante l'analisi dello scontrino**")
        st.info(
            "Si è verificato un problema imprevisto. Puoi riprovare oppure "
            "inserire i dati manualmente nel form sottostante."
        )
        if rt:
            with st.expander("🔍 Dettaglio tecnico"):
                st.caption(rt)

def _render_history_tab(records, year):

    if not records:
        st.info(f"Nessun dato nel {year}.")
        return

    df = grids.build_fuel_dataframe(records)
    # Formattazione per visualizzazione
    df['Data'] = pd.to_datetime(df['Data'])
    df_show = df.copy()
    df_show['Data'] = df_show['Data'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        df_show.drop(columns=["_obj"]), 
        width="stretch", hide_index=True,
        column_config={
            "ID": None, 
            "Pieno": st.column_config.TextColumn(width="small"),
            "Km/L": st.column_config.TextColumn(width="small"),
            "Descrizione": st.column_config.TextColumn(width="medium")
        }
    )

def _render_management_tab(db, user, all_records, years, def_idx, settings):
    if not all_records:
        st.info("Nessun dato modificabile.")
        return

    # Selezione Record
    mgmt_year = st.selectbox("Anno Gestione", years, index=def_idx, key="mgmt_year_sel")
    recs_year = [r for r in all_records if r.date.year == mgmt_year]
    
    if not recs_year:
        st.warning("Nessun record in questo anno.")
        return

    opts = {f"{r.date.strftime('%d/%m')} - {r.total_km}km (€ {r.total_cost:.2f})": r.id for r in recs_year}
    sel_label = st.selectbox("Seleziona Record", list(opts.keys()))
    target_id = opts[sel_label] if sel_label else None
    
    # Pulsanti Azione
    c1, c2 = st.columns(2)
    if c1.button("✏️ Modifica", width="stretch"):
        st.session_state.active_operation = "edit"
        st.session_state.selected_record_id = target_id
        st.rerun()
    if c2.button("❌ Elimina", type="primary", width="stretch"):
        st.session_state.active_operation = "delete"
        st.session_state.selected_record_id = target_id
        st.rerun()
    
    # Gestione Pannelli Operativi
    if st.session_state.active_operation and st.session_state.selected_record_id == target_id:
        target_rec = next((r for r in all_records if r.id == target_id), None)
        if target_rec:
            st.divider()
            if st.session_state.active_operation == "edit":
                _handle_edit_flow(db, user.id, target_rec, settings) # Passa user.id
            elif st.session_state.active_operation == "delete":
                _handle_delete_flow(db, user.id, target_id)

def _handle_edit_flow(db, user_id, rec, settings):
    st.markdown(f"**Modifica Record:** {rec.date}")
    
    with st.form("fuel_form_edit"):
        # Calcolo range dinamico per lo slider del prezzo
        min_pe, max_pe = max(0.0, rec.price_per_liter-0.5), rec.price_per_liter+0.5
        
        # Se il record esistente ha un costo superiore al limite impostato nei settings,
        # il max_value del form deve essere il maggiore tra il limite configurato e il valore attuale.
        safe_max_cost = max(float(settings.max_total_cost), float(rec.total_cost))
        
        # Riutilizzo componente UI form
        edit_data = forms.render_refueling_inputs(
            rec.date, rec.total_km, rec.price_per_liter, rec.total_cost, 
            rec.is_full_tank, rec.notes, 
            min_pe, max_pe, 
            safe_max_cost,
            last_km_known=rec.total_km 
        )
        
        if st.form_submit_button("Aggiorna", type="primary", width="stretch"):
            # Nota: In edit non controlliamo "last_km" stretto come in insert per flessibilità
            new_liters = edit_data['cost'] / edit_data['price'] if edit_data['price'] > 0 else 0
            
            changes = {
                "date": edit_data['date'], "total_km": edit_data['km'], 
                "price_per_liter": edit_data['price'], "total_cost": edit_data['cost'], 
                "liters": new_liters, "is_full_tank": edit_data['full'], "notes": edit_data['notes']
            }
            
            crud.update_refueling(db, user_id, rec.id, changes)
            st.success("Record aggiornato!")
            st.session_state.active_operation = None
            st.rerun()
            
    if st.button("Annulla", width="stretch"):
        st.session_state.active_operation = None; st.rerun()

def _handle_delete_flow(db, user_id, record_id):
    st.error("Sei sicuro di voler eliminare definitivamente questo record?")
    cd1, cd2 = st.columns(2)
    if cd1.button("Sì, Elimina", type="primary", width="stretch"):
        crud.delete_refueling(db, user_id, record_id)
        st.success("Eliminato."); st.session_state.active_operation = None; st.rerun()
    if cd2.button("No, Annulla", width="stretch"):
        st.session_state.active_operation = None; st.rerun()