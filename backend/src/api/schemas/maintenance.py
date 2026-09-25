"""
Modelli Pydantic per il dominio Manutenzione (contratti dati HTTP).
Definisce le strutture per la registrazione interventi, aggiornamenti parziali e scadenze predittive.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


class MaintenanceBase(BaseModel):
    """Campi anagrafici base di una registrazione di manutenzione."""
    date: dt.date = Field(..., description="Data dell'intervento di manutenzione")
    total_km: int = Field(..., gt=0, description="Chilometraggio del veicolo al momento dell'intervento")
    expense_type: str = Field(..., min_length=1, description="Categoria o tipologia di spesa (es. Tagliando, Revisione, Gomme)")
    cost: float = Field(..., ge=0, description="Importo speso in Euro (può essere 0 per garanzie o controlli gratuiti)")
    description: Optional[str] = Field(None, description="Dettaglio lavorazioni, officina o ricambi utilizzati")
    expiry_km: Optional[int] = Field(None, gt=0, description="Chilometraggio previsto per la prossima scadenza")
    expiry_date: Optional[dt.date] = Field(None, description="Data prevista per la prossima scadenza")


class MaintenanceCreate(MaintenanceBase):
    """Payload per l'inserimento di una nuova voce di manutenzione."""
    pass


class MaintenanceUpdate(BaseModel):
    """Payload per l'aggiornamento parziale di una voce di manutenzione esistente."""
    date: Optional[dt.date] = None
    total_km: Optional[int] = Field(None, gt=0)
    expense_type: Optional[str] = Field(None, min_length=1)
    cost: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    expiry_km: Optional[int] = Field(None, gt=0)
    expiry_date: Optional[dt.date] = None


class MaintenanceResponse(MaintenanceBase):
    """Rappresentazione completa del record di manutenzione restituita dal backend."""
    id: int
    user_id: str

    model_config = {"from_attributes": True}


class MaintenanceDeadlineResponse(BaseModel):
    """Rappresentazione di una scadenza attiva con stima predittiva e stato di priorità semaforica."""
    id: int
    expense_type: str
    date: dt.date
    total_km: int
    cost: float
    expiry_km: Optional[int] = None
    expiry_date: Optional[dt.date] = None
    km_left: Optional[int] = Field(None, description="Chilometri residui prima del superamento del limite")
    days_left: Optional[int] = Field(None, description="Giorni solari residui prima della scadenza temporale")
    priority: int = Field(..., description="Priorità di allarme: 1 (Scaduto), 2 (Imminente), 3 (Regolare)")
    status_color: str = Field(..., description="Codice colore esadecimale per UI a semaforo")
    predicted_date: Optional[dt.date] = Field(None, description="Data stimata di raggiungimento del limite chilometrico")
