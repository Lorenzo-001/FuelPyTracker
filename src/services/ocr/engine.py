import base64
import json
import streamlit as st
from datetime import datetime
from openai import OpenAI, APIConnectionError, RateLimitError, AuthenticationError, APIError
from typing import Optional
from .models import ReceiptData

# =============================================================================
# CONFIGURAZIONE CLIENT OPENAI
# =============================================================================
# Recupera la chiave dai secrets. Se non c'è, il client sarà None.
_api_key = st.secrets.get("openai", {}).get("api_key")
client = OpenAI(api_key=_api_key) if _api_key else None

def is_openai_enabled() -> bool:
    """
    Restituisce True se OpenAI è configurato correttamente e pronto all'uso.
    Utile per nascondere/mostrare componenti UI condizionali.
    """
    return client is not None

def analyze_receipt(file_buffer) -> ReceiptData:
    """
    Invia l'immagine dello scontrino a OpenAI GPT-4o e restituisce dati strutturati.
    
    Args:
        file_buffer: Oggetto file-like (bytes) caricato da Streamlit.
        
    Returns:
        ReceiptData: DTO popolato con i dati estratti (o errore nel campo raw_text).
    """
    # 1. Controllo Pre-Flight
    if not client:
        return ReceiptData(raw_text="ERRORE: API Key OpenAI mancante in .streamlit/secrets.toml")

    try:
        # 2. Preparazione Immagine (Encoding Base64)
        # OpenAI richiede l'immagine come stringa base64
        base64_image = _encode_image_to_base64(file_buffer)

        # 3. Definizione del Prompt (System Instruction)
        # Istruiamo l'AI a comportarsi come un parser JSON rigoroso
        system_prompt = """
        Sei un motore OCR intelligente specializzato in scontrini carburante italiani.
        Analizza l'immagine fornita ed estrai i dati nel seguente formato JSON rigoroso:
        {
            "total_cost": float o null (Costo totale in Euro),
            "price_per_liter": float o null (Prezzo al litro),
            "date": "YYYY-MM-DD" o null,
            "station_name": string o null (Es. "Eni Station", "Q8")
        }
        Regole:
        - Se hai Totale e Litri ma manca il Prezzo/L, calcolalo (Totale / Litri).
        - Ignora punti fedeltà o altri prodotti non carburante se possibile.
        - Restituisci SOLO il JSON, nessun markdown.
        """

        # 4. Chiamata API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Estrai i dati da questo scontrino."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
            temperature=0.0, # Determinismo massimo
            response_format={ "type": "json_object" } # Forza output JSON
        )

        # 5. Parsing & Pulizia Risposta
        content = response.choices[0].message.content
        
        # Rimuove eventuali backtick markdown se l'AI sbaglia formato
        content = content.replace("```json", "").replace("```", "").strip()
        
        data_dict = json.loads(content)
        return _map_json_to_model(data_dict)

    # --- GESTIONE ERRORI SPECIFICI ---
    
    except AuthenticationError:
        return ReceiptData(raw_text="⛔ ERRORE AUTH: La tua API Key di OpenAI non è valida o è scaduta.")

    except RateLimitError:
        return ReceiptData(raw_text="💸 ERRORE QUOTA: Credito OpenAI esaurito o limite richieste raggiunto. Controlla il billing.")

    except APIConnectionError:
        return ReceiptData(raw_text="🌐 ERRORE RETE: Impossibile connettersi ai server OpenAI. Controlla la connessione internet.")

    except APIError as e:
        return ReceiptData(raw_text=f"🔥 ERRORE SERVER: Problema interno di OpenAI. Riprova più tardi. ({str(e)})")

    except json.JSONDecodeError:
        return ReceiptData(raw_text="🤖 ERRORE AI: L'intelligenza artificiale ha risposto con un formato non valido.")

    except Exception as e:
        return ReceiptData(raw_text=f"❌ ERRORE IMPREVISTO: {str(e)}")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _encode_image_to_base64(file_buffer) -> str:
    """Legge il buffer e lo converte in stringa base64 utf-8."""
    # Assicuriamoci di essere all'inizio del file
    file_buffer.seek(0)
    return base64.b64encode(file_buffer.read()).decode('utf-8')

def _map_json_to_model(data: dict) -> ReceiptData:
    """Converte il dizionario JSON grezzo nell'oggetto ReceiptData."""
    rd = ReceiptData()
    rd.raw_text = "Analisi GPT-4o Completata" # Feedback positivo
    
    # Mapping sicuro con controlli di tipo
    try:
        if data.get("total_cost"):
            rd.total_cost = float(data["total_cost"])
            
        if data.get("price_per_liter"):
            rd.price_per_liter = float(data["price_per_liter"])
            
        if data.get("date"):
            # Gestione formati data imprevisti
            try:
                rd.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
            except ValueError:
                pass # Data non valida, resta None
        
        rd.station_name = data.get("station_name")
        
        # Calcolo derivato Litri (se non presenti o per verifica)
        if rd.total_cost > 0 and rd.price_per_liter > 0:
            rd.liters = round(rd.total_cost / rd.price_per_liter, 2)
            
    except Exception as e:
        rd.raw_text = f"Errore Mapping Dati: {e}"
        
    return rd