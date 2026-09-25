import os
from pathlib import Path
import base64
import json
import toml
# pyrefly: ignore [missing-import]
import streamlit as st
from datetime import datetime
# pyrefly: ignore [missing-import]
from openai import OpenAI, APIConnectionError, RateLimitError, AuthenticationError, APIError
from typing import Optional
from .models import ReceiptData
from src.demo import is_demo_mode, mock_analyze_receipt


# =============================================================================
# CONFIGURAZIONE CLIENT OPENAI
# =============================================================================

def _get_openai_key() -> str | None:
    """Recupera la chiave API di OpenAI da variabili d'ambiente, st.secrets o secrets.toml."""
    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key

    try:
        key = st.secrets.get("openai", {}).get("api_key")
        if key:
            return str(key)
    except Exception:
        pass

    try:
        candidates = [
            Path(__file__).resolve().parents[3] / ".streamlit" / "secrets.toml",
            Path.cwd() / "backend" / ".streamlit" / "secrets.toml",
            Path.cwd() / ".streamlit" / "secrets.toml",
        ]
        for candidate in candidates:
            if candidate.is_file():
                data = toml.load(candidate)
                k = data.get("openai", {}).get("api_key")
                if k:
                    return str(k)
    except Exception:
        pass

    return None


def get_openai_client() -> OpenAI | None:
    """Restituisce un'istanza del client OpenAI o None se non configurato."""
    api_key = _get_openai_key()
    return OpenAI(api_key=api_key) if api_key else None


client = get_openai_client()


def is_openai_enabled() -> bool:
    """Restituisce True se OpenAI è configurato e pronto all'uso."""
    return client is not None or bool(_get_openai_key())


def analyze_receipt(file_buffer) -> ReceiptData:
    """
    Invia l'immagine dello scontrino a OpenAI GPT-4o e restituisce dati strutturati.
    
    Args:
        file_buffer: Oggetto file-like (bytes) caricato da Streamlit o FastAPI.
        
    Returns:
        ReceiptData: DTO popolato con i dati estratti (o errore nel campo raw_text).
    """
    # Demo Mode: short-circuit prima di qualsiasi chiamata esterna.
    if is_demo_mode():
        return mock_analyze_receipt()

    # 1. Controllo Pre-Flight
    global client
    if client is None and _get_openai_key():
        client = get_openai_client()

    if not client:
        return ReceiptData(raw_text="ERRORE: API Key OpenAI mancante in backend/.env o variabili d'ambiente.")

    try:
        base64_image = _encode_image_to_base64(file_buffer)

        system_prompt = """
        Sei un motore OCR avanzato specializzato nell'estrazione precisa di dati da scontrini e ricevute di carburante italiani.
        Analizza con la massima accuratezza l'immagine dello scontrino fornita ed estrai i dati nel seguente formato JSON rigoroso:
        {
            "total_cost": float o null,
            "price_per_liter": float o null,
            "liters": float o null,
            "date": "YYYY-MM-DD" o null,
            "station_name": string o null
        }

        REGOLE ED ESEMPI PER GLI SCONTRINI ITALIANI:
        1. LITRI / VOLUME / QUANTITÀ ("liters"):
           - Cerca diciture come: "Litri", "Volume", "Q.tà", "Quantità", "Erogato", "Vol.", "L.", "LT", "Litri Erogati".
           - Esempio: "VOL. 25,40 L" o "LITRI: 33.15" -> estrai 25.40 o 33.15.
        2. PREZZO UNITARIO ("price_per_liter"):
           - Cerca diciture come: "Prezzo/L", "€/L", "Euro/L", "Prezzo Unitario", "Prezzo Unit.", "€/Lt", "P.U.".
           - Esempio: "1,789 €/L" o "PREZZO 1.829" -> estrai 1.789 o 1.829.
        3. IMPORTO TOTALE ("total_cost"):
           - Cerca il totale pagato: "Totale", "Importo", "Totale Euro", "Totale Dovuto", "Totale Complessivo", "Pagato".
           - Se presente un pagamento elettronico o contanti ("Bancomat", "Carta", "POS"), l'importo corrisponde al totale della transazione.
           - Esempio: "TOTALE € 50,00" -> estrai 50.00.
        4. DATA DEL RIFORNIMENTO ("date"):
           - Fai molta attenzione al formato delle date italiane (GG/MM/AAAA o GG-MM-AA).
           - Non confondere il giorno con l'anno! Se leggi "20/01/26", significa 20 gennaio 2026 -> restituisci "2026-01-20".
           - Se l'anno è indicato a due cifre (es. '24, '25, '26), convertilo nel formato completo (es. 2024, 2025, 2026).
        5. DISTRIBUTORE / STAZIONE ("station_name"):
           - Identifica il marchio/insegna presente nell'intestazione o nel corpo dello scontrino (es. "Eni Station", "Q8", "IP Gruppo API", "Tamoil", "Esso", "Repsol", "Beyfin", "Retitalia", "Vega", "Conad", ecc.).
           - Includi anche l'indirizzo o località se visibile (es. "Q8 - Tangenziale Est").
        6. TRIADE MATEMATICA:
           - Se leggi 2 valori su 3 tra (Totale, Prezzo/L, Litri), calcola con precisione il 3° valore mancante (Totale = Litri * Prezzo/L).
        7. FORMATO:
           - Restituisci SOLO il JSON conforme allo schema, senza spiegazioni né blocchi markdown.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Estrai i dati da questo scontrino di carburante."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
            temperature=0.0,  # Determinismo massimo
            response_format={"type": "json_object"},  # Forza output JSON
        )

        content = response.choices[0].message.content
        # Strip eventuali backtick markdown in caso di formato errato
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
    file_buffer.seek(0)
    return base64.b64encode(file_buffer.read()).decode('utf-8')

def _map_json_to_model(data: dict) -> ReceiptData:
    """Converte il dizionario JSON grezzo nell'oggetto ReceiptData con autoguarigione matematica."""
    rd = ReceiptData()
    rd.raw_text = "Analisi GPT-4o Completata"
    
    try:
        if data.get("total_cost") is not None:
            rd.total_cost = float(data["total_cost"])
            
        if data.get("price_per_liter") is not None:
            rd.price_per_liter = float(data["price_per_liter"])

        if data.get("liters") is not None:
            rd.liters = float(data["liters"])
            
        if data.get("date"):
            try:
                rd.date = datetime.strptime(str(data["date"]).strip(), "%Y-%m-%d").date()
            except ValueError:
                pass
        
        rd.station_name = data.get("station_name")
        
        # Triade di autoguarigione matematica:
        if rd.total_cost > 0 and rd.price_per_liter > 0 and (rd.liters is None or rd.liters <= 0):
            rd.liters = round(rd.total_cost / rd.price_per_liter, 2)
        elif rd.total_cost > 0 and rd.liters > 0 and (rd.price_per_liter is None or rd.price_per_liter <= 0):
            rd.price_per_liter = round(rd.total_cost / rd.liters, 3)
        elif rd.liters > 0 and rd.price_per_liter > 0 and (rd.total_cost is None or rd.total_cost <= 0):
            rd.total_cost = round(rd.liters * rd.price_per_liter, 2)
            
    except Exception as e:
        rd.raw_text = f"Errore Mapping Dati: {e}"
        
    return rd