"""
Modelli Pydantic per il dominio Promemoria & Routine (/api/reminders).
Definisce le strutture per la creazione, aggiornamento, monitoraggio scadenze e log di esecuzione.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field, model_validator


class ReminderBase(BaseModel):
    """Campi informativi di base di un promemoria per controlli periodici."""
    title: str = Field(..., min_length=1, description="Titolo o categoria del promemoria (es. Controllo Olio, Pressione Gomme)")
    frequency_km: Optional[int] = Field(None, gt=0, description="Frequenza di controllo in chilometri percorsi")
    frequency_days: Optional[int] = Field(None, gt=0, description="Frequenza di controllo in giorni solari")
    notes: Optional[str] = Field(None, description="Istruzioni o note operative specifiche per l'attività")


class ReminderCreate(ReminderBase):
    """Payload per la creazione di un nuovo promemoria."""
    current_km: Optional[int] = Field(None, gt=0, description="Chilometraggio iniziale di riferimento (opzionale, default ultimo noto)")
    current_date: Optional[dt.date] = Field(None, description="Data di inizio monitoraggio (default oggi)")

    @model_validator(mode="after")
    def validate_frequency(self) -> ReminderCreate:
        if not self.frequency_km and not self.frequency_days:
            raise ValueError("È necessario specificare almeno una frequenza di controllo (chilometri o giorni).")
        return self


class ReminderUpdate(BaseModel):
    """Payload per la modifica dei parametri di un promemoria esistente."""
    title: Optional[str] = Field(None, min_length=1)
    frequency_km: Optional[int] = Field(None, gt=0)
    frequency_days: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class ReminderResponse(ReminderBase):
    """Rappresentazione completa del promemoria arricchita con lo stato di avanzamento calcolato."""
    id: int
    user_id: str
    last_km_check: Optional[int] = None
    last_date_check: Optional[dt.date] = None
    is_active: bool = True
    target_km: Optional[int] = Field(None, description="Chilometraggio obiettivo previsto per il prossimo controllo")
    target_date: Optional[dt.date] = Field(None, description="Data obiettivo prevista per il prossimo controllo")
    remaining_km: Optional[int] = Field(None, description="Chilometri residui (negativo se superato)")
    remaining_days: Optional[int] = Field(None, description="Giorni residui (negativo se scaduto)")
    progress: float = Field(0.0, description="Percentuale di avanzamento normalizzata (da 0.0 a 1.0)")
    is_overdue: bool = Field(False, description="True se il promemoria ha superato il limite chilometrico o temporale")
    status_message: str = Field("", description="Messaggio testuale human-friendly per UI")

    model_config = {"from_attributes": True}


class ReminderExecutionRequest(BaseModel):
    """Payload per l'azione 'Mark as Done' di completamento del controllo di routine."""
    check_date: dt.date = Field(default_factory=dt.date.today, description="Data effettiva in cui è stato eseguito il controllo")
    check_km: Optional[int] = Field(None, gt=0, description="Chilometri del veicolo al momento dell'esecuzione (default ultimo noto)")
    notes: Optional[str] = Field("", description="Note o riscontri sul controllo effettuato")


class ReminderHistoryResponse(BaseModel):
    """Storico dell'avvenuto completamento di un controllo di routine."""
    id: int
    reminder_id: int
    user_id: str
    date_checked: dt.date
    km_checked: int
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
