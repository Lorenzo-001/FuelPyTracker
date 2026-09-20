"""
Modelli Pydantic per il dominio Report, Esportazione & Importazione (/api/reports).
Definisce le strutture per statistiche export, parametri libretto PDF e pipeline di anteprima/commit staging.
"""
from __future__ import annotations

import datetime as dt
from typing import List, Optional, Dict, Any
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


class ExportStatsResponse(BaseModel):
    """Statistiche rapide per il pannello di download ed esportazione dati."""
    refuelings_count: int = Field(..., description="Numero totale di rifornimenti disponibili per l'export")
    maintenances_count: int = Field(..., description="Numero totale di interventi di manutenzione registrati")
    years_available: List[int] = Field(default_factory=list, description="Anni solari in cui sono presenti registrazioni")


class PDFReportRequest(BaseModel):
    """Parametri di testata e anagrafica veicolo per la compilazione del Libretto Digitale in PDF."""
    owner_name: str = Field(..., min_length=1, max_length=100, description="Nome e cognome dell'intestatario del veicolo")
    plate: str = Field(..., min_length=1, max_length=20, description="Targa del veicolo (es. 'AB123CD')")
    car_model: str = Field(..., min_length=1, max_length=100, description="Marca e modello del veicolo (es. 'Fiat Panda 1.2')")
    year: Optional[int] = Field(None, description="Anno solare di riferimento (opzionale, default storico completo)")


class ImportPreviewResponse(BaseModel):
    """Risultato dell'analisi preliminare di staging del file caricato (CSV o Excel)."""
    success: bool
    global_error: Optional[str] = None
    fuel_rows: List[Dict[str, Any]] = Field(default_factory=list, description="Righe analizzate del foglio Rifornimenti")
    fuel_summary: Dict[str, int] = Field(default_factory=dict, description="Conteggi di sintesi per stato (nuovo, modifica, warning, errore)")
    maintenance_rows: List[Dict[str, Any]] = Field(default_factory=list, description="Righe analizzate del foglio Manutenzioni")
    maintenance_summary: Dict[str, int] = Field(default_factory=dict, description="Conteggi di sintesi per stato (nuovo, modifica, warning, errore)")


class ImportCommitRowFuel(BaseModel):
    """Singola riga rifornimento confermata dall'utente per il salvataggio."""
    date: dt.date
    total_km: int = Field(..., gt=0)
    price_per_liter: float = Field(..., gt=0)
    total_cost: float = Field(..., gt=0)
    liters: float = Field(..., gt=0)
    is_full_tank: bool = True
    notes: Optional[str] = None
    db_id: Optional[int] = None
    status: str = Field("Nuovo", description="'Nuovo', 'Modifica', 'Warning' o 'OK'")


class ImportCommitRowMaintenance(BaseModel):
    """Singola riga manutenzione confermata dall'utente per il salvataggio."""
    date: dt.date
    total_km: int = Field(..., gt=0)
    expense_type: str = Field(..., min_length=1)
    cost: float = Field(..., gt=0)
    description: Optional[str] = None
    expiry_km: Optional[int] = None
    expiry_date: Optional[dt.date] = None
    db_id: Optional[int] = None
    status: str = Field("Nuovo", description="'Nuovo', 'Modifica', 'Warning' o 'OK'")


class ImportCommitRequest(BaseModel):
    """Payload per il commit transazionale delle righe validate."""
    fuel_rows: List[ImportCommitRowFuel] = Field(default_factory=list)
    maintenance_rows: List[ImportCommitRowMaintenance] = Field(default_factory=list)


class ImportCommitResponse(BaseModel):
    """Esito del commit delle righe importate a database."""
    success: bool
    fuel_inserted: int = 0
    fuel_updated: int = 0
    maintenance_inserted: int = 0
    maintenance_updated: int = 0
    message: str = ""
