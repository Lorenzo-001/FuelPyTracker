from .models import ReceiptData
# Importiamo la funzione dal NUOVO engine
from .engine import analyze_receipt 

def process_receipt_image(uploaded_file) -> ReceiptData:
    """
    Entry point della pipeline OCR.
    Usa OpenAI GPT-4o per l'estrazione.
    """
    if not uploaded_file:
        return ReceiptData()
    
    # Delega diretta all'engine AI
    return analyze_receipt(uploaded_file)