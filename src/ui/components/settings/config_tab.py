import streamlit as st
from src.database.core import get_db
from src.database import crud
from src.config import DEFAULTS
from src.demo import writes_disabled


@st.dialog("Conferma Eliminazione")
def show_delete_dialog(index, label_name, session_key: str, editing_key: str):
    st.write(f"Sei sicuro di voler rimuovere la categoria **{label_name}** dalla lista?")
    st.warning("Ricordati di salvare le configurazioni dopo la conferma.")
    
    col1, col2 = st.columns(2)
    if col1.button("Sì, elimina", type="primary", width='stretch'):
        st.session_state[session_key].pop(index)
        # Gestione reset indice se stiamo cancellando l'elemento in modifica
        if st.session_state[editing_key] == index:
            st.session_state[editing_key] = -1
        elif st.session_state[editing_key] > index:
            st.session_state[editing_key] -= 1
        st.rerun()
        
    if col2.button("Annulla", width='stretch'):
        st.rerun()


def _render_category_editor(session_key: str, editing_key: str, add_placeholder: str = "Nuova categoria"):
    """Componente riutilizzabile per gestire una lista di categorie (add/edit/delete card)."""
    # A. AREA AGGIUNTA
    c_add_in, c_add_btn = st.columns([5, 1], vertical_alignment="bottom")
    new_label_input = c_add_in.text_input(
        "Nuova Categoria", placeholder=add_placeholder,
        label_visibility="collapsed", key=f"{session_key}_new_input"
    )
    if c_add_btn.form_submit_button("➕", key=f"{session_key}_add_btn", help="Aggiungi", type="secondary", width='stretch', disabled=writes_disabled()):
        if new_label_input:
            clean_val = new_label_input.strip()
            if clean_val not in st.session_state[session_key]:
                st.session_state[session_key].append(clean_val)
                st.rerun()
            else:
                st.warning("Categoria già presente nella lista.")
        else:
            st.error("⚠️ Inserisci un nome per la categoria prima di aggiungere.")

    st.write("")

    # B. LISTA CARD
    if not st.session_state[session_key]:
        st.info("Nessuna categoria.")

    for i, label in enumerate(st.session_state[session_key]):
        is_editing = (st.session_state[editing_key] == i)

        with st.container(border=True):
            c_text, c_actions_block = st.columns([4, 1.2], vertical_alignment="center")

            with c_text:
                if is_editing:
                    edit_val = st.text_input(
                        f"ed_{session_key}_{i}", value=label,
                        label_visibility="collapsed"
                    )
                else:
                    st.markdown(f"**{label}**")

            with c_actions_block:
                b1, b2 = st.columns(2)

                if is_editing:
                    if b1.form_submit_button("✅", key=f"s_{session_key}_{i}", width='stretch', disabled=writes_disabled()):
                        if edit_val:
                            st.session_state[session_key][i] = edit_val.strip()
                            st.session_state[editing_key] = -1
                            st.rerun()
                    if b2.form_submit_button("❌", key=f"u_{session_key}_{i}", width='stretch'):
                        st.session_state[editing_key] = -1
                        st.rerun()
                else:
                    if b1.form_submit_button("✏️", key=f"e_{session_key}_{i}", help="Modifica", width='stretch', disabled=writes_disabled()):
                        st.session_state[editing_key] = i
                        st.rerun()
                    if b2.form_submit_button("❌", key=f"d_{session_key}_{i}", help="Elimina", width='stretch', disabled=writes_disabled()):
                        show_delete_dialog(i, label, session_key, editing_key)


def render(user):
    """Gestisce i parametri globali dell'app per l'utente specifico."""
    db = next(get_db())
    settings = crud.get_settings(db, user.id)
    
    # --- 1. GESTIONE STATO LOCALE (Labels) ---
    if "settings_temp_labels" not in st.session_state:
        st.session_state.settings_temp_labels = list(
            settings.reminder_types or DEFAULTS.SETTINGS.REMINDER_TYPES
        )
    
    if "settings_temp_maint_types" not in st.session_state:
        st.session_state.settings_temp_maint_types = list(
            settings.maintenance_types or DEFAULTS.SETTINGS.MAINTENANCE_TYPES
        )
    
    # Reset indici
    if "settings_editing_idx" not in st.session_state:
        st.session_state.settings_editing_idx = -1
    
    if "settings_editing_maint_idx" not in st.session_state:
        st.session_state.settings_editing_maint_idx = -1

    st.subheader("Parametri Inserimento & Sicurezza")
    
    st.markdown("""
    > **Guida alla Configurazione:**
    > 1. **Range Prezzo:** Imposta la tolleranza dello slider per il prezzo carburante.
    > 2. **Tetto Spesa:** Fissa un limite massimo di sicurezza per evitare errori di digitazione (es. 500€).
    > 3. **Soglia Allerta:** Ricevi un avviso se accumuli troppi rifornimenti parziali consecutivi.
    > 4. **Categorie Promemoria:** Voci selezionabili nel menu a tendina quando crei un nuovo Promemoria periodico.
    > 5. **Categorie Manutenzione:** Voci selezionabili nel campo "Categoria" durante l'inserimento manuale e l'importazione Excel degli interventi.
    > 6. **Salvataggio:** Tutte le modifiche vengono salvate al click del bottone "Salva Configurazioni".
    """)
    
    st.write("") 

    with st.form("config_form"):
        # --- SEZIONE 1: Limiti Numerici ---
        st.markdown("##### 🎚️ Limiti Inserimento")
        
        new_range = st.number_input(
            "Range Oscillazione Prezzo (+/- €)", 
            min_value=0.01, max_value=0.50, 
            value=settings.price_fluctuation_cents,
            step=0.01, format="%.2f",
            help="Margine di tolleranza dello slider prezzo. Un valore di 0.15 significa che lo slider copre il prezzo storico ±0.15 €."
        )
        
        new_max = st.number_input(
            "Tetto Massimo Spesa per Pieno (€)", 
            min_value=50.0, max_value=500.0, 
            value=settings.max_total_cost,
            step=10.0, format="%.2f",
            help="Costo massimo consentito per un rifornimento. Record superiori a questo valore vengono segnalati come Warning nell’importazione."
        )
        
        new_alert_threshold = st.number_input(
            "Soglia Allerta Parziali Cumulati (€)",
            min_value=20.0, max_value=500.0,
            value=settings.max_accumulated_partial_cost,
            step=10.0, format="%.2f",
            help="Somma massima di rifornimenti parziali consecutivi prima di ricevere un avviso nella dashboard."
        )
        
        st.divider()
        
        # --- SEZIONE 1b: Limiti Importazione Excel ---
        st.markdown("##### 📊 Limiti Importazione Excel")
        st.caption(
            "Soglie usate durante la validazione dei dati Excel importati. "
            "**Warning** (riga importabile ma segnalata) vs **Errore** (riga bloccata, correzione richiesta)."
        )
        
        c_kml1, c_kml2 = st.columns(2)
        
        new_kml_min = c_kml1.number_input(
            "Consumo Minimo km/L ⚠️ Warning",
            min_value=0.5, max_value=20.0,
            value=float(settings.import_kml_min or DEFAULTS.SETTINGS.IMPORT.KML_MIN),
            step=0.5, format="%.1f",
            help="Consumo minimo plausibile per singolo rifornimento. Valori **sotto** questa soglia generano un `Warning`: la riga viene importata ma evidenziata. Abbassa per furgoni pesanti o veicoli ad alto consumo (es. 2.0 km/L)."
        )
        
        new_kml_max = c_kml2.number_input(
            "Consumo Massimo km/L ⚠️ Warning",
            min_value=5.0, max_value=100.0,
            value=float(settings.import_kml_max or DEFAULTS.SETTINGS.IMPORT.KML_MAX),
            step=1.0, format="%.1f",
            help="Consumo massimo plausibile per singolo rifornimento. Valori **sopra** questa soglia generano un `Warning`: la riga viene importata ma evidenziata. Alza per auto ibride molto efficienti (es. 35 km/L)."
        )
        
        c_kml3, c_kml4 = st.columns(2)
        
        new_kml_error = c_kml3.number_input(
            "Soglia km/L Impossibile ❌ Errore",
            min_value=50.0, max_value=500.0,
            value=float(settings.import_kml_error or DEFAULTS.SETTINGS.IMPORT.KML_ERROR),
            step=10.0, format="%.0f",
            help="Soglia assoluta oltre la quale il consumo è fisicamente impossibile per qualsiasi veicolo stradale. Valori **sopra** questa soglia generano un `Errore` bloccante. Default: 150 km/L (nessun veicolo convenzionale supera questo valore)."
        )
        
        new_kmd_max = c_kml4.number_input(
            "Velocità Massima km/giorno ❌ Errore",
            min_value=500.0, max_value=5000.0,
            value=float(settings.import_kmd_max or DEFAULTS.SETTINGS.IMPORT.KMD_MAX),
            step=100.0, format="%.0f",
            help="Distanza massima percorribile in un giorno. Se tra un rifornimento e il precedente i km percorsi superano (giorni × questo limite), la riga viene bloccata come `Errore`. Default: 1500 km/giorno, limite realistico anche per guide intercontinentali."
        )
        
        st.divider()
        st.markdown("##### 🏷️ Gestione Categorie")

        cat_tab_rem, cat_tab_maint = st.tabs(["🔔 Categorie Promemoria", "🔧 Categorie Manutenzione"])

        # ── TAB 1: CATEGORIE PROMEMORIA ───────────────────────────────────
        with cat_tab_rem:
            st.caption(
                "Voci selezionabili nel menu a tendina **Categoria** quando crei un nuovo Promemoria periodico. "
                "Aggiungine di personalizzate in base alle esigenze del tuo veicolo."
            )
            _render_category_editor(
                session_key="settings_temp_labels",
                editing_key="settings_editing_idx",
                add_placeholder="Es. Filtro Abitacolo",
            )

        # ── TAB 2: CATEGORIE MANUTENZIONE ─────────────────────────────────
        with cat_tab_maint:
            st.caption(
                "Voci selezionabili nel campo **Categoria** durante l'inserimento manuale di un intervento "
                "e nella colonna \"Tipo Intervento\" in fase di importazione da file Excel. "
                "Assicurati che tutte le categorie nei tuoi file di backup siano presenti qui."
            )
            _render_category_editor(
                session_key="settings_temp_maint_types",
                editing_key="settings_editing_maint_idx",
                add_placeholder="Es. Freni",
            )

        st.write("")
        st.write("")
        
        # --- SALVATAGGIO FINALE ---
        if writes_disabled():
            st.warning("🔒 Modalità Demo: Modifiche disabilitate per sicurezza.")
        elif st.form_submit_button("💾 Salva Configurazioni", type="primary", width='stretch'):
            crud.update_settings(
                db, user.id, 
                new_range, 
                new_max, 
                new_alert_threshold,
                st.session_state.settings_temp_labels,
                maintenance_labels=st.session_state.settings_temp_maint_types,
                kml_min=new_kml_min,
                kml_max=new_kml_max,
                kml_error=new_kml_error,
                kmd_max=new_kmd_max
            )
            del st.session_state["settings_temp_labels"]
            del st.session_state["settings_editing_idx"]
            del st.session_state["settings_temp_maint_types"]
            del st.session_state["settings_editing_maint_idx"]
            
            st.success("✅ Configurazioni salvate con successo!")
            st.rerun()
    
    db.close()
