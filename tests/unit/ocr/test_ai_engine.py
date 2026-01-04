import pytest
from unittest.mock import patch, MagicMock
from src.services.ocr import engine
from src.services.ocr.models import ReceiptData

# JSON Finto che simula la risposta di GPT-4o
MOCK_OPENAI_RESPONSE_JSON = """
{
    "total_cost": 50.00,
    "price_per_liter": 1.759,
    "date": "2024-01-15",
    "station_name": "Eni Station Test"
}
"""

@patch("src.services.ocr.engine.client") # 1. Mockiamo il client OpenAI intero
def test_analyze_receipt_success(mock_client):
    """
    Verifica che l'engine processi correttamente la risposta dell'AI.
    NON chiama veramente OpenAI (Costo: 0€).
    """
    # SETUP DEL MOCK
    # Creiamo una catena di oggetti finti per simulare:
    # client.chat.completions.create().choices[0].message.content
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = MOCK_OPENAI_RESPONSE_JSON
    
    # Diciamo al mock: "Quando vieni chiamato, restituisci questo oggetto finto"
    mock_client.chat.completions.create.return_value = mock_completion

    # Creiamo un file finto (buffer di bytes)
    fake_file = MagicMock()
    fake_file.read.return_value = b"fake_image_bytes"

    # ESECUZIONE
    result = engine.analyze_receipt(fake_file)

    # ASSERZIONI
    assert isinstance(result, ReceiptData)
    assert result.total_cost == 50.00
    assert result.price_per_liter == 1.759
    assert result.station_name == "Eni Station Test"
    # Verifica che i litri siano stati calcolati matematicamente (50 / 1.759)
    assert result.liters == 28.43 
    
    # Verifica che il metodo create sia stato chiamato una volta sola
    mock_client.chat.completions.create.assert_called_once()