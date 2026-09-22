"""
Router API per il dominio Promemoria & Routine (/api/reminders).
Fornisce gestione attività periodiche, monitoraggio scadenze dinamiche e log esecuzioni ("Mark as Done").
"""
from __future__ import annotations

import datetime as dt
from datetime import date, timedelta
from typing import List, Optional
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from src.database.models import Reminder, ReminderHistory
from src.database import crud
from src.api.deps import get_db, get_current_user_id
from src.api.schemas.reminders import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderExecutionRequest,
    ReminderHistoryResponse,
)

router = APIRouter(prefix="/reminders", tags=["Reminders"])


def _enrich_reminder(rem: Reminder, current_km: int) -> ReminderResponse:
    """Arricchisce il modello Reminder con i calcoli di avanzamento, target e scadenza."""
    target_km = None
    target_date = None
    remaining_km = None
    remaining_days = None
    progress = 0.0
    is_overdue = False
    status_message = ""

    today = date.today()

    if rem.frequency_km:
        last = rem.last_km_check if rem.last_km_check is not None else current_km
        target_km = last + rem.frequency_km
        diff = current_km - last
        overrun = current_km - target_km
        remaining_km = target_km - current_km

        if diff >= rem.frequency_km:
            progress = 1.0
            is_overdue = True
            status_message = f"Limite superato da {overrun} Km"
        else:
            progress = max(0.0, diff / rem.frequency_km) if rem.frequency_km > 0 else 0.0
            status_message = f"Mancano {remaining_km} Km alla scadenza"

    elif rem.frequency_days:
        last = rem.last_date_check if rem.last_date_check is not None else today
        target_date = last + timedelta(days=rem.frequency_days)
        diff_days = (today - last).days
        overrun_days = (today - target_date).days
        remaining_days = (target_date - today).days

        if diff_days >= rem.frequency_days:
            progress = 1.0
            is_overdue = True
            status_message = f"Scaduto da {overrun_days} giorni"
        else:
            progress = max(0.0, diff_days / rem.frequency_days) if rem.frequency_days > 0 else 0.0
            status_message = f"Mancano {remaining_days} giorni alla scadenza"

    return ReminderResponse(
        id=rem.id,
        user_id=rem.user_id,
        title=rem.title,
        frequency_km=rem.frequency_km,
        frequency_days=rem.frequency_days,
        last_km_check=rem.last_km_check,
        last_date_check=rem.last_date_check,
        is_active=rem.is_active,
        notes=rem.notes,
        target_km=target_km,
        target_date=target_date,
        remaining_km=remaining_km,
        remaining_days=remaining_days,
        progress=round(progress, 2),
        is_overdue=is_overdue,
        status_message=status_message,
    )


@router.get(
    "",
    response_model=List[ReminderResponse],
    summary="Elenco promemoria attivi",
    description="Recupera tutti i promemoria attivi dell'utente, arricchiti con barra di avanzamento e stato di scadenza.",
)
def get_reminders(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> List[ReminderResponse]:
    reminders = (
        db.query(Reminder)
        .filter(Reminder.user_id == user_id, Reminder.is_active == True)
        .order_by(Reminder.id.asc())
        .all()
    )
    refuelings = crud.get_all_refuelings(db, user_id)
    current_km = max((r.total_km for r in refuelings), default=0)
    return [_enrich_reminder(rem, current_km) for rem in reminders]


@router.post(
    "",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea un nuovo promemoria",
)
def create_reminder(
    payload: ReminderCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ReminderResponse:
    refuelings = crud.get_all_refuelings(db, user_id)
    current_km = payload.current_km or max((r.total_km for r in refuelings), default=0)
    current_date = payload.current_date or date.today()

    new_rem = crud.create_reminder(
        db=db,
        user_id=user_id,
        title=payload.title,
        frequency_km=payload.frequency_km,
        frequency_days=payload.frequency_days,
        current_km=current_km,
        current_date=current_date,
        notes=payload.notes,
    )
    return _enrich_reminder(new_rem, current_km)


@router.get(
    "/history",
    response_model=List[ReminderHistoryResponse],
    summary="Storico esecuzioni controlli di routine",
    description="Recupera gli ultimi interventi periodici contrassegnati come completati.",
)
def get_reminder_history(
    limit: int = Query(20, ge=1, le=100, description="Numero massimo di record da restituire"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> List[ReminderHistoryResponse]:
    records = crud.get_reminder_history(db, user_id, limit=limit)
    return [ReminderHistoryResponse.model_validate(r) for r in records]


@router.get(
    "/{record_id}",
    response_model=ReminderResponse,
    summary="Dettaglio singolo promemoria",
)
def get_reminder(
    record_id: int = Path(..., description="ID del promemoria"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ReminderResponse:
    rem = db.query(Reminder).filter(Reminder.id == record_id, Reminder.user_id == user_id).first()
    if not rem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promemoria non trovato")
    refuelings = crud.get_all_refuelings(db, user_id)
    current_km = max((r.total_km for r in refuelings), default=0)
    return _enrich_reminder(rem, current_km)


@router.put(
    "/{record_id}",
    response_model=ReminderResponse,
    summary="Modifica parametri promemoria",
)
def update_reminder(
    record_id: int = Path(..., description="ID del promemoria"),
    payload: ReminderUpdate = ...,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ReminderResponse:
    rem = db.query(Reminder).filter(Reminder.id == record_id, Reminder.user_id == user_id).first()
    if not rem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promemoria non trovato")

    update_dict = payload.model_dump(exclude_unset=True)
    if "title" in update_dict and update_dict["title"]:
        rem.title = update_dict["title"]
    if "frequency_km" in update_dict:
        rem.frequency_km = update_dict["frequency_km"]
    if "frequency_days" in update_dict:
        rem.frequency_days = update_dict["frequency_days"]
    if "is_active" in update_dict and update_dict["is_active"] is not None:
        rem.is_active = update_dict["is_active"]
    if "notes" in update_dict:
        rem.notes = update_dict["notes"]

    db.commit()
    db.refresh(rem)

    try:
        import streamlit as st
        st.cache_data.clear()
    except Exception:
        pass

    refuelings = crud.get_all_refuelings(db, user_id)
    current_km = max((r.total_km for r in refuelings), default=0)
    return _enrich_reminder(rem, current_km)


@router.delete(
    "/{record_id}",
    summary="Elimina un promemoria",
)
def delete_reminder(
    record_id: int = Path(..., description="ID del promemoria"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    success = crud.delete_reminder(db, user_id, record_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promemoria non trovato")
    return {"message": "Promemoria eliminato con successo", "success": True}


@router.post(
    "/{record_id}/complete",
    response_model=ReminderResponse,
    summary="Registra completamento routine ('Mark as Done')",
    description="Registra l'avvenuto controllo nello storico (ReminderHistory) e resetta il conteggio per il prossimo ciclo.",
)
def complete_reminder(
    record_id: int = Path(..., description="ID del promemoria"),
    payload: ReminderExecutionRequest = ...,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ReminderResponse:
    rem = db.query(Reminder).filter(Reminder.id == record_id, Reminder.user_id == user_id).first()
    if not rem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promemoria non trovato")

    refuelings = crud.get_all_refuelings(db, user_id)
    last_known_km = max((r.total_km for r in refuelings), default=rem.last_km_check or 0)
    effective_km = payload.check_km if payload.check_km is not None else last_known_km

    crud.log_reminder_execution(
        db=db,
        user_id=user_id,
        reminder_id=record_id,
        check_date=payload.check_date,
        check_km=effective_km,
        notes=payload.notes or "",
    )

    db.refresh(rem)
    return _enrich_reminder(rem, effective_km)
