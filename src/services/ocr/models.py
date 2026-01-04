from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class ReceiptData:
    """
    Data Transfer Object (DTO) per i dati estratti dallo scontrino.
    Serve a standardizzare l'output del parser.
    """
    date: Optional[date] = None # type: ignore
    total_cost: float = 0.0
    price_per_liter: float = 0.0
    liters: float = 0.0
    station_name: Optional[str] = None
    raw_text: str = ""  # Utile per debugging