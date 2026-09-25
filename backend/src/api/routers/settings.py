"""
Router API per il dominio Impostazioni & Configurazioni Utente (/api/settings).
Gestisce i parametri di sicurezza, le soglie di importazione, opzioni AI e le categorie personalizzate.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from src.database import crud
from src.api.deps import get_db, get_current_user_id
from src.api.schemas.settings import (
    AppSettingsResponse,
    AppSettingsUpdate,
    CategoryOperationRequest,
)

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get(
    "",
    response_model=AppSettingsResponse,
    summary="Recupera le impostazioni dell'utente",
    description="Restituisce le soglie operative, i limiti di importazione e le categorie personalizzate dell'utente.",
)
def get_user_settings(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> AppSettingsResponse:
    settings = crud.get_settings(db, user_id)
    return AppSettingsResponse.model_validate(settings)


@router.put(
    "",
    response_model=AppSettingsResponse,
    summary="Aggiorna le impostazioni dell'utente",
    description="Modifica parzialmente o totalmente le soglie di spesa, i limiti di tolleranza e i parametri di sistema.",
)
def update_user_settings(
    payload: AppSettingsUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> AppSettingsResponse:
    current = crud.get_settings(db, user_id)

    updated = crud.update_settings(
        db=db,
        user_id=user_id,
        fluctuation=payload.price_fluctuation_cents if payload.price_fluctuation_cents is not None else current.price_fluctuation_cents,
        max_cost=payload.max_total_cost if payload.max_total_cost is not None else current.max_total_cost,
        alert_threshold=payload.max_accumulated_partial_cost if payload.max_accumulated_partial_cost is not None else current.max_accumulated_partial_cost,
        custom_labels=payload.reminder_types if payload.reminder_types is not None else current.reminder_types,
        maintenance_labels=payload.maintenance_types if payload.maintenance_types is not None else current.maintenance_types,
        kml_min=payload.import_kml_min if payload.import_kml_min is not None else current.import_kml_min,
        kml_max=payload.import_kml_max if payload.import_kml_max is not None else current.import_kml_max,
        kml_error=payload.import_kml_error if payload.import_kml_error is not None else current.import_kml_error,
        kmd_max=payload.import_kmd_max if payload.import_kmd_max is not None else current.import_kmd_max,
        ocr_add_station_to_notes=payload.ocr_add_station_to_notes if payload.ocr_add_station_to_notes is not None else current.ocr_add_station_to_notes,
        ocr_add_liters_to_notes=payload.ocr_add_liters_to_notes if payload.ocr_add_liters_to_notes is not None else current.ocr_add_liters_to_notes,
        vehicle_name=payload.vehicle_name if payload.vehicle_name is not None else getattr(current, "vehicle_name", None),
        vehicle_plate=payload.vehicle_plate if payload.vehicle_plate is not None else getattr(current, "vehicle_plate", None),
        vehicle_fuel_type=payload.vehicle_fuel_type if payload.vehicle_fuel_type is not None else getattr(current, "vehicle_fuel_type", None),
    )
    return AppSettingsResponse.model_validate(updated)


@router.post(
    "/reminder-categories",
    response_model=AppSettingsResponse,
    summary="Aggiunge una categoria per i promemoria",
)
def add_reminder_category(
    payload: CategoryOperationRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> AppSettingsResponse:
    settings = crud.get_settings(db, user_id)
    categories = list(settings.reminder_types or [])
    new_cat = payload.category.strip()

    if new_cat in categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La categoria '{new_cat}' è già presente tra i promemoria.",
        )

    categories.append(new_cat)
    updated = crud.update_settings(
        db=db,
        user_id=user_id,
        fluctuation=settings.price_fluctuation_cents,
        max_cost=settings.max_total_cost,
        alert_threshold=settings.max_accumulated_partial_cost,
        custom_labels=categories,
        maintenance_labels=settings.maintenance_types or [],
        kml_min=settings.import_kml_min,
        kml_max=settings.import_kml_max,
        kml_error=settings.import_kml_error,
        kmd_max=settings.import_kmd_max,
        ocr_add_station_to_notes=settings.ocr_add_station_to_notes,
        ocr_add_liters_to_notes=settings.ocr_add_liters_to_notes,
    )
    return AppSettingsResponse.model_validate(updated)


@router.delete(
    "/reminder-categories/{category_name}",
    response_model=AppSettingsResponse,
    summary="Rimuove una categoria dai promemoria",
)
def delete_reminder_category(
    category_name: str = Path(..., description="Nome della categoria da eliminare"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> AppSettingsResponse:
    settings = crud.get_settings(db, user_id)
    categories = list(settings.reminder_types or [])

    if category_name not in categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoria promemoria '{category_name}' non trovata.",
        )

    categories.remove(category_name)
    updated = crud.update_settings(
        db=db,
        user_id=user_id,
        fluctuation=settings.price_fluctuation_cents,
        max_cost=settings.max_total_cost,
        alert_threshold=settings.max_accumulated_partial_cost,
        custom_labels=categories,
        maintenance_labels=settings.maintenance_types or [],
        kml_min=settings.import_kml_min,
        kml_max=settings.import_kml_max,
        kml_error=settings.import_kml_error,
        kmd_max=settings.import_kmd_max,
        ocr_add_station_to_notes=settings.ocr_add_station_to_notes,
        ocr_add_liters_to_notes=settings.ocr_add_liters_to_notes,
    )
    return AppSettingsResponse.model_validate(updated)


@router.post(
    "/maintenance-categories",
    response_model=AppSettingsResponse,
    summary="Aggiunge una categoria di manutenzione",
)
def add_maintenance_category(
    payload: CategoryOperationRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> AppSettingsResponse:
    settings = crud.get_settings(db, user_id)
    categories = list(settings.maintenance_types or [])
    new_cat = payload.category.strip()

    if new_cat in categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La categoria '{new_cat}' è già presente tra le manutenzioni.",
        )

    categories.append(new_cat)
    updated = crud.update_settings(
        db=db,
        user_id=user_id,
        fluctuation=settings.price_fluctuation_cents,
        max_cost=settings.max_total_cost,
        alert_threshold=settings.max_accumulated_partial_cost,
        custom_labels=settings.reminder_types or [],
        maintenance_labels=categories,
        kml_min=settings.import_kml_min,
        kml_max=settings.import_kml_max,
        kml_error=settings.import_kml_error,
        kmd_max=settings.import_kmd_max,
        ocr_add_station_to_notes=settings.ocr_add_station_to_notes,
        ocr_add_liters_to_notes=settings.ocr_add_liters_to_notes,
    )
    return AppSettingsResponse.model_validate(updated)


@router.delete(
    "/maintenance-categories/{category_name}",
    response_model=AppSettingsResponse,
    summary="Rimuove una categoria di manutenzione",
)
def delete_maintenance_category(
    category_name: str = Path(..., description="Nome della tipologia da eliminare"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> AppSettingsResponse:
    settings = crud.get_settings(db, user_id)
    categories = list(settings.maintenance_types or [])

    if category_name not in categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipologia manutenzione '{category_name}' non trovata.",
        )

    categories.remove(category_name)
    updated = crud.update_settings(
        db=db,
        user_id=user_id,
        fluctuation=settings.price_fluctuation_cents,
        max_cost=settings.max_total_cost,
        alert_threshold=settings.max_accumulated_partial_cost,
        custom_labels=settings.reminder_types or [],
        maintenance_labels=categories,
        kml_min=settings.import_kml_min,
        kml_max=settings.import_kml_max,
        kml_error=settings.import_kml_error,
        kmd_max=settings.import_kmd_max,
        ocr_add_station_to_notes=settings.ocr_add_station_to_notes,
        ocr_add_liters_to_notes=settings.ocr_add_liters_to_notes,
    )
    return AppSettingsResponse.model_validate(updated)
