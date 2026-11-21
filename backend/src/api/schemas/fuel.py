"""
Modelli Pydantic per il dominio Carburante (contratti dati HTTP).
Definisce le strutture di validazione per inserimento, modifica, calcolo consumi e OCR.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


class RefuelingBase(BaseModel):
    """Campi anagrafici base di un rifornimento."""
    date: dt.date = Field(..., description="Data del rifornimento")
    total_km: int = Field(..., gt=0, description="Chilometri totali del contachilometri")
    price_per_liter: float = Field(..., gt=0, description="Prezzo al litro in Euro")
    total_cost: float = Field(..., gt=0, description="Spesa totale sostenuta in Euro")
    liters: float = Field(..., gt=0, description="Quantità di carburante erogata in litri")
    is_full_tank: bool = Field(True, description="True se è stato effettuato un pieno, False se parziale")
    notes: Optional[str] = Field(None, description="Note aggiuntive, dettagli o nome distributore")


class RefuelingCreate(RefuelingBase):
    """Payload inviato dal client per la creazione di un nuovo rifornimento."""
    pass


class RefuelingUpdate(BaseModel):
    """Payload per l'aggiornamento parziale di un rifornimento esistente."""
    date: Optional[dt.date] = None
    total_km: Optional[int] = Field(None, gt=0)
    price_per_liter: Optional[float] = Field(None, gt=0)
    total_cost: Optional[float] = Field(None, gt=0)
    liters: Optional[float] = Field(None, gt=0)
    is_full_tank: Optional[bool] = None
    notes: Optional[str] = None


class RefuelingResponse(RefuelingBase):
    """Rappresentazione completa del rifornimento arricchita con le metriche calcolate."""
    id: int
    user_id: str
    delta_km: Optional[int] = Field(None, description="Chilometri percorsi rispetto al rifornimento precedente")
    km_per_liter: Optional[float] = Field(None, description="Efficienza calcolata con algoritmo Full-to-Full (km/L)")
    days_since_last: Optional[int] = Field(None, description="Giorni trascorsi dall'ultimo rifornimento")

    model_config = {"from_attributes": True}


class RefuelingValidationRequest(BaseModel):
    """Dati da validare prima dell'inserimento effettivo nel form."""
    date: dt.date
    km: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    cost: float = Field(..., gt=0)
    is_full: bool = True


class RefuelingValidationResponse(BaseModel):
    """Esito del controllo pre-flight di coerenza chilometrica e cronologica."""
    is_valid: bool
    message: str = ""
    prev_km: Optional[int] = None
    next_km: Optional[int] = None


class OCRScanResponse(BaseModel):
    """Risultato strutturato della scansione AI dello scontrino."""
    success: bool
    total_cost: Optional[float] = None
    price_per_liter: Optional[float] = None
    liters: Optional[float] = None
    date: Optional[dt.date] = None
    station_name: Optional[str] = None
    raw_text: Optional[str] = None
