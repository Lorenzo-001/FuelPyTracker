"""
Router API per il dominio Manutenzione (/api/maintenance).
Fornisce operazioni CRUD con isolamento tenant, gestione scadenze predittive ed elenco categorie.
"""
from __future__ import annotations

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from src.database.models import Maintenance
from src.database import crud
from src.api.deps import get_db, get_current_user_id
from src.api.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceUpdate,
    MaintenanceResponse,
    MaintenanceDeadlineResponse,
)
from src.services.business import maintenance_logic
from src.services.business.prediction import calculate_daily_usage_rate, predict_reach_date

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.get(
    "",
    response_model=List[MaintenanceResponse],
    summary="Elenco storico manutenzioni",
    description="Recupera tutti gli interventi registrati dall'utente, con filtri opzionali per anno solare e categoria.",
)
def get_maintenances(
    year: Optional[int] = Query(None, description="Filtra gli interventi per anno solare"),
    expense_type: Optional[str] = Query(None, description="Filtra per categoria o tipologia spesa"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> List[MaintenanceResponse]:
    records = crud.get_all_maintenances(db, user_id)
    if year is not None:
        records = [r for r in records if r.date.year == year]
    if expense_type:
        records = [r for r in records if r.expense_type == expense_type]
    return [MaintenanceResponse.model_validate(r) for r in records]


@router.post(
    "",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra un nuovo intervento di manutenzione",
)
def create_maintenance(
    payload: MaintenanceCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> MaintenanceResponse:
    new_record = crud.create_maintenance(
        db=db,
        user_id=user_id,
        date_obj=payload.date,
        total_km=payload.total_km,
        expense_type=payload.expense_type,
        cost=payload.cost,
        description=payload.description,
        expiry_km=payload.expiry_km,
        expiry_date=payload.expiry_date,
    )
    return MaintenanceResponse.model_validate(new_record)


@router.get(
    "/categories",
    response_model=List[str],
    summary="Elenco categorie utilizzate",
    description="Restituisce la lista distinta di tutte le tipologie di spesa registrate dall'utente.",
)
def get_categories(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> List[str]:
    records = crud.get_all_maintenances(db, user_id)
    return maintenance_logic.get_all_categories(records)


@router.get(
    "/deadlines",
    response_model=List[MaintenanceDeadlineResponse],
    summary="Scadenze attive e manutenzione predittiva",
    description="Restituisce le scadenze chilometriche e fiscali attive con stima della data di raggiungimento basata sul rateo d'uso.",
)
def get_deadlines(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> List[MaintenanceDeadlineResponse]:
    records = crud.get_all_maintenances(db, user_id)
    refuelings = crud.get_all_refuelings(db, user_id)
    last_known_km = max((r.total_km for r in refuelings), default=0)
    daily_rate = calculate_daily_usage_rate(refuelings)
    today = date.today()

    candidates = []
    for r in records:
        if not r.expiry_km and not r.expiry_date:
            continue

        km_left = (r.expiry_km - last_known_km) if r.expiry_km else None
        days_left = (r.expiry_date - today).days if r.expiry_date else None

        # Logica a semaforo
        is_expired_km = km_left is not None and km_left < 0
        is_expired_days = days_left is not None and days_left < 0

        if is_expired_km or is_expired_days:
            status_color = "#dc3545"  # Rosso
            priority = 1
        elif (km_left is not None and km_left <= 1000) or (days_left is not None and days_left <= 30):
            status_color = "#ffc107"  # Giallo
            priority = 2
        else:
            status_color = "#28a745"  # Verde
            priority = 3

        predicted = None
        if r.expiry_km and not r.expiry_date and daily_rate > 0:
            predicted = predict_reach_date(last_known_km, r.expiry_km, daily_rate)

        candidates.append(
            MaintenanceDeadlineResponse(
                id=r.id,
                expense_type=r.expense_type,
                date=r.date,
                total_km=r.total_km,
                cost=r.cost,
                expiry_km=r.expiry_km,
                expiry_date=r.expiry_date,
                km_left=km_left,
                days_left=days_left,
                priority=priority,
                status_color=status_color,
                predicted_date=predicted,
            )
        )

    # Deduplicazione per categoria: preserva la scadenza a priorità maggiore (più urgente)
    unique_deadlines = {}
    for c in candidates:
        if c.expense_type not in unique_deadlines or c.priority < unique_deadlines[c.expense_type].priority:
            unique_deadlines[c.expense_type] = c

    # Ordina per priorità (1 -> 2 -> 3)
    return sorted(list(unique_deadlines.values()), key=lambda x: x.priority)


@router.get(
    "/{record_id}",
    response_model=MaintenanceResponse,
    summary="Dettaglio singolo intervento di manutenzione",
)
def get_maintenance(
    record_id: int = Path(..., description="ID del record"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> MaintenanceResponse:
    record = db.query(Maintenance).filter(Maintenance.id == record_id, Maintenance.user_id == user_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manutenzione non trovata")
    return MaintenanceResponse.model_validate(record)


@router.put(
    "/{record_id}",
    response_model=MaintenanceResponse,
    summary="Aggiorna un intervento di manutenzione",
)
def update_maintenance(
    record_id: int = Path(..., description="ID del record"),
    payload: MaintenanceUpdate = ...,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> MaintenanceResponse:
    existing = db.query(Maintenance).filter(Maintenance.id == record_id, Maintenance.user_id == user_id).first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manutenzione non trovata")

    update_data = payload.model_dump(exclude_unset=True)
    if update_data:
        crud.update_maintenance(db, user_id, record_id, update_data)

    refreshed = db.query(Maintenance).filter(Maintenance.id == record_id).first()
    return MaintenanceResponse.model_validate(refreshed)


@router.delete(
    "/{record_id}",
    summary="Elimina un intervento di manutenzione",
)
def delete_maintenance(
    record_id: int = Path(..., description="ID del record"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    success = crud.delete_maintenance(db, user_id, record_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manutenzione non trovata")
    return {"message": "Manutenzione eliminata con successo", "success": True}
