"""
Router API per la gestione dei Rifornimenti e scansione OCR (/api/fuel).
Fornisce operazioni CRUD con isolamento tenant, calcolo metriche Full-to-Full e parsing AI scontrini.
"""
from __future__ import annotations

import io
import logging
from typing import List, Optional
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, Query, Path, File, UploadFile, status
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from src.database.models import Refueling
from src.database import crud
from src.api.deps import get_db, get_current_user_id
from src.api.schemas.fuel import (
    RefuelingCreate,
    RefuelingUpdate,
    RefuelingResponse,
    RefuelingValidationRequest,
    RefuelingValidationResponse,
    OCRScanResponse,
)
from src.services.business.calculations import calculate_stats
from src.services.business import fuel_logic
from src.services.ocr.engine import analyze_receipt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fuel", tags=["Fuel"])


def _to_response_dto(record: Refueling, all_records: List[Refueling]) -> RefuelingResponse:
    """Helper per mappare il modello ORM al DTO arricchito con le metriche Full-to-Full."""
    stats = calculate_stats(record, all_records)
    km_l = stats.get("km_per_liter")
    if km_l is not None:
        km_l = round(km_l, 2)
    return RefuelingResponse(
        id=record.id,
        user_id=record.user_id,
        date=record.date,
        total_km=record.total_km,
        price_per_liter=record.price_per_liter,
        total_cost=record.total_cost,
        liters=record.liters,
        is_full_tank=record.is_full_tank,
        notes=record.notes,
        delta_km=stats.get("delta_km"),
        km_per_liter=km_l,
        days_since_last=stats.get("days_since_last"),
    )


@router.get(
    "",
    response_model=List[RefuelingResponse],
    summary="Elenco storico dei rifornimenti",
    description="Recupera tutti i rifornimenti dell'utente autenticato, arricchiti con consumo km/L e delta km.",
)
def get_refuelings(
    year: Optional[int] = Query(None, description="Filtra i rifornimenti per anno solare"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> List[RefuelingResponse]:
    all_records = crud.get_all_refuelings(db, user_id)
    target_records = [r for r in all_records if r.date.year == year] if year else all_records
    return [_to_response_dto(r, all_records) for r in target_records]


@router.post(
    "",
    response_model=RefuelingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra un nuovo rifornimento",
    description="Valida la coerenza cronologica dei chilometri ed effettua la persistenza a database.",
)
def create_refueling(
    payload: RefuelingCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> RefuelingResponse:
    all_records = crud.get_all_refuelings(db, user_id)
    validation_payload = {
        "km": payload.total_km,
        "date": payload.date,
        "price": payload.price_per_liter,
        "cost": payload.total_cost,
        "is_full": payload.is_full_tank,
    }
    
    # Validazione di business rule (date e chilometri non decrescenti)
    is_valid, error_msg = fuel_logic.validate_refueling(validation_payload, all_records)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    new_record = crud.create_refueling(
        db=db,
        user_id=user_id,
        date_obj=payload.date,
        total_km=payload.total_km,
        price_per_liter=payload.price_per_liter,
        total_cost=payload.total_cost,
        liters=payload.liters,
        is_full_tank=payload.is_full_tank,
        notes=payload.notes,
    )
    
    # Ricalcola metriche con lo storico aggiornato
    updated_records = crud.get_all_refuelings(db, user_id)
    return _to_response_dto(new_record, updated_records)


@router.get(
    "/{record_id}",
    response_model=RefuelingResponse,
    summary="Recupera un singolo rifornimento",
)
def get_refueling(
    record_id: int = Path(..., description="ID del record"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> RefuelingResponse:
    record = db.query(Refueling).filter(Refueling.id == record_id, Refueling.user_id == user_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rifornimento non trovato")
    all_records = crud.get_all_refuelings(db, user_id)
    return _to_response_dto(record, all_records)


@router.put(
    "/{record_id}",
    response_model=RefuelingResponse,
    summary="Aggiorna un rifornimento esistente",
)
def update_refueling(
    record_id: int = Path(..., description="ID del record"),
    payload: RefuelingUpdate = ...,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> RefuelingResponse:
    existing = db.query(Refueling).filter(Refueling.id == record_id, Refueling.user_id == user_id).first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rifornimento non trovato")

    update_data = payload.model_dump(exclude_unset=True)
    if update_data:
        # Verifica coerenza chilometrica escludendo il record in modifica
        other_records = [r for r in crud.get_all_refuelings(db, user_id) if r.id != record_id]
        check_dict = {
            "km": update_data.get("total_km", existing.total_km),
            "date": update_data.get("date", existing.date),
            "price": update_data.get("price_per_liter", existing.price_per_liter),
            "cost": update_data.get("total_cost", existing.total_cost),
            "is_full": update_data.get("is_full_tank", existing.is_full_tank),
        }
        is_valid, msg = fuel_logic.validate_refueling(check_dict, other_records)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        crud.update_refueling(db, user_id, record_id, update_data)

    refreshed = db.query(Refueling).filter(Refueling.id == record_id).first()
    all_records = crud.get_all_refuelings(db, user_id)
    return _to_response_dto(refreshed, all_records)


@router.delete(
    "/{record_id}",
    summary="Elimina un rifornimento",
)
def delete_refueling(
    record_id: int = Path(..., description="ID del record"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    success = crud.delete_refueling(db, user_id, record_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rifornimento non trovato")
    return {"message": "Rifornimento eliminato con successo", "success": True}


@router.post(
    "/validate",
    response_model=RefuelingValidationResponse,
    summary="Pre-flight check di coerenza chilometri e date",
    description="Permette alla UI di convalidare i dati inseriti dall'utente prima dell'invio finale.",
)
def validate_refueling(
    payload: RefuelingValidationRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> RefuelingValidationResponse:
    all_records = crud.get_all_refuelings(db, user_id)
    check_payload = {
        "km": payload.km,
        "date": payload.date,
        "price": payload.price,
        "cost": payload.cost,
        "is_full": payload.is_full,
    }
    is_valid, msg = fuel_logic.validate_refueling(check_payload, all_records)
    neighbors = crud.get_neighbors(db, user_id, payload.date)

    return RefuelingValidationResponse(
        is_valid=is_valid,
        message=msg,
        prev_km=neighbors["prev"].total_km if neighbors.get("prev") else None,
        next_km=neighbors["next"].total_km if neighbors.get("next") else None,
    )


@router.post(
    "/ocr",
    response_model=OCRScanResponse,
    summary="Scansione OCR scontrino carburante",
    description="Estrae prezzo, costo, data e distributore dall'immagine dello scontrino tramite OpenAI GPT-4o.",
)
async def scan_receipt_ocr(
    file: UploadFile = File(..., description="Immagine dello scontrino (JPEG, PNG o WebP)"),
) -> OCRScanResponse:
    content_type = file.content_type or ""
    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il file caricato deve essere un'immagine valida (JPEG, PNG, WebP).",
        )

    file_bytes = await file.read()
    buffer = io.BytesIO(file_bytes)
    
    try:
        receipt_data = analyze_receipt(buffer)
        return OCRScanResponse(
            success=True,
            total_cost=receipt_data.total_cost,
            price_per_liter=receipt_data.price_per_liter,
            liters=receipt_data.liters,
            date=receipt_data.date,
            station_name=receipt_data.station_name,
            raw_text=receipt_data.raw_text,
        )
    except Exception as exc:
        logger.error("Errore durante l'elaborazione OCR: %s", exc)
        return OCRScanResponse(
            success=False,
            raw_text=f"Errore durante l'analisi OCR: {exc}",
        )
