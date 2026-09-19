"""OCR modal for receipt smart-scan (fuel add flow)."""
import streamlit as st
from datetime import date
from src.services.ocr import process_receipt_image


@st.dialog("📸 Scansione Smart Scontrino")
def open_ocr_dialog():
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
                    show_ocr_error(data.raw_text)


def show_ocr_error(raw_text: str):
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
