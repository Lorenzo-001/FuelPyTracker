"""
Router API per il dominio Report, Esportazione & Importazione (/api/reports).
Fornisce download Excel multi-sheet, template vuoto, generazione libretto PDF e pipeline di importazione con anteprima di staging.
"""
from __future__ import annotations

import io
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Response, status
from sqlalchemy.orm import Session

from src.database import crud
from src.api.deps import get_db, get_current_user_id
from src.api.schemas.reports import (
    ExportStatsResponse,
    PDFReportRequest,
    ImportPreviewResponse,
    ImportCommitRequest,
    ImportCommitResponse,
)
from src.services.data.exporters import reports, templates, pdf_generator
from src.services.data.importers import manager

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "/stats",
    response_model=ExportStatsResponse,
    summary="Statistiche dati esportabili",
    description="Restituisce il numero totale di rifornimenti e manutenzioni disponibili per il download.",
)
def get_export_stats(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ExportStatsResponse:
    fuels = crud.get_all_refuelings(db, user_id)
    maints = crud.get_all_maintenances(db, user_id)
    years = sorted(list(set(m.date.year for m in maints)), reverse=True)

    return ExportStatsResponse(
        refuelings_count=len(fuels),
        maintenances_count=len(maints),
        years_available=years,
    )


@router.get(
    "/excel",
    summary="Download archivio Excel completo (Rifornimenti & Manutenzioni)",
    description="Genera e scarica un file .xlsx multi-sheet con formattazione e stili professionali.",
    response_class=Response,
)
def download_excel_report(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    fuels = crud.get_all_refuelings(db, user_id)
    maints = crud.get_all_maintenances(db, user_id)

    if not fuels and not maints:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nessun dato presente nel database da esportare.",
        )

    excel_bytes = reports.generate_excel_report(db, user_id)
    filename = f"fuelpytracker_backup_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/template",
    summary="Download modello Excel vuoto pre-formattato",
    description="Restituisce il file .xlsx pre-compilato con le intestazioni standard per facilitare il caricamento massivo.",
    response_class=Response,
)
def download_excel_template():
    template_bytes = templates.generate_empty_template()
    filename = "FuelPyTracker_Template.xlsx"

    return Response(
        content=template_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post(
    "/pdf",
    summary="Generazione Libretto Manutenzione Digitale in PDF",
    description="Compila il documento PDF ufficiale con scheda tecnica veicolo, aggregati di spesa e registro storico interventi.",
    response_class=Response,
)
def generate_pdf_booklet(
    payload: PDFReportRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    pdf_bytes = pdf_generator.generate_maintenance_report(
        db=db,
        user_id=user_id,
        owner_name=payload.owner_name,
        plate=payload.plate,
        car_model=payload.car_model,
        year=payload.year,
    )

    year_suffix = f"_{payload.year}" if payload.year else "_completo"
    filename = f"Libretto_Manutenzione_{payload.plate.upper().strip()}{year_suffix}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post(
    "/import/preview",
    response_model=ImportPreviewResponse,
    summary="Anteprima e staging del file di importazione (CSV / Excel)",
    description="Analizza il file caricato, rileva i fogli e valida ciascuna riga segnalando nuovi inserimenti, modifiche, warning ed errori.",
)
async def preview_import_file(
    file: UploadFile = File(..., description="File Excel (.xlsx) o CSV (.csv)"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ImportPreviewResponse:
    filename = file.filename or ""
    if not (filename.endswith(".xlsx") or filename.endswith(".csv")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato non supportato. Caricare esclusivamente file con estensione .xlsx o .csv.",
        )

    file_bytes = await file.read()
    buffer = io.BytesIO(file_bytes)
    buffer.name = filename

    parse_result = manager.parse_upload_file(db, user_id, buffer)
    if "global_error" in parse_result:
        return ImportPreviewResponse(
            success=False,
            global_error=parse_result["global_error"],
        )

    fuel_records: List[Dict[str, Any]] = []
    fuel_summary: Dict[str, int] = {}
    maint_records: List[Dict[str, Any]] = []
    maint_summary: Dict[str, int] = {}

    # 1. Processing Rifornimenti
    if "fuel" in parse_result:
        df_fuel, err_fuel = parse_result["fuel"]
        if err_fuel:
            return ImportPreviewResponse(success=False, global_error=err_fuel)
        if not df_fuel.empty:
            df_fuel_clean = df_fuel.copy()
            # Converti Timestamp in stringhe ISO
            if "Data" in df_fuel_clean.columns:
                df_fuel_clean["Data"] = df_fuel_clean["Data"].astype(str)
            fuel_records = df_fuel_clean.to_dict(orient="records")
            fuel_summary = df_fuel["Stato"].value_counts().to_dict() if "Stato" in df_fuel else {}

    # 2. Processing Manutenzione
    if "maintenance" in parse_result:
        df_maint, err_maint = parse_result["maintenance"]
        if err_maint:
            return ImportPreviewResponse(success=False, global_error=err_maint)
        if not df_maint.empty:
            df_maint_clean = df_maint.copy()
            if "Data" in df_maint_clean.columns:
                df_maint_clean["Data"] = df_maint_clean["Data"].astype(str)
            if "Scadenza Data" in df_maint_clean.columns:
                df_maint_clean["Scadenza Data"] = df_maint_clean["Scadenza Data"].astype(str)
            maint_records = df_maint_clean.to_dict(orient="records")
            maint_summary = df_maint["Stato"].value_counts().to_dict() if "Stato" in df_maint else {}

    return ImportPreviewResponse(
        success=True,
        fuel_rows=fuel_records,
        fuel_summary=fuel_summary,
        maintenance_rows=maint_records,
        maintenance_summary=maint_summary,
    )


@router.post(
    "/import/commit",
    response_model=ImportCommitResponse,
    summary="Salvataggio transazionale delle righe importate",
    description="Persiste a database le righe confermate dall'utente gestendo nuovi inserimenti e aggiornamenti.",
)
def commit_imported_rows(
    payload: ImportCommitRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> ImportCommitResponse:
    f_ins, f_upd = 0, 0
    m_ins, m_upd = 0, 0

    # 1. Commit Rifornimenti
    for row in payload.fuel_rows:
        if row.status == "Modifica" and row.db_id:
            crud.update_refueling(db, user_id, row.db_id, {
                "price_per_liter": row.price_per_liter,
                "total_cost": row.total_cost,
                "liters": row.liters,
                "is_full_tank": row.is_full_tank,
                "notes": row.notes,
            })
            f_upd += 1
        elif row.status in ["Nuovo", "OK", "Warning"]:
            crud.create_refueling(
                db=db,
                user_id=user_id,
                date_obj=row.date,
                total_km=row.total_km,
                price_per_liter=row.price_per_liter,
                total_cost=row.total_cost,
                liters=row.liters,
                is_full_tank=row.is_full_tank,
                notes=row.notes,
            )
            f_ins += 1

    # 2. Commit Manutenzioni
    for row in payload.maintenance_rows:
        if row.status == "Modifica" and row.db_id:
            crud.update_maintenance(db, user_id, row.db_id, {
                "expense_type": row.expense_type,
                "cost": row.cost,
                "description": row.description,
                "expiry_km": row.expiry_km,
                "expiry_date": row.expiry_date,
            })
            m_upd += 1
        elif row.status in ["Nuovo", "OK", "Warning"]:
            crud.create_maintenance(
                db=db,
                user_id=user_id,
                date_obj=row.date,
                total_km=row.total_km,
                expense_type=row.expense_type,
                cost=row.cost,
                description=row.description,
                expiry_km=row.expiry_km,
                expiry_date=row.expiry_date,
            )
            m_ins += 1

    return ImportCommitResponse(
        success=True,
        fuel_inserted=f_ins,
        fuel_updated=f_upd,
        maintenance_inserted=m_ins,
        maintenance_updated=m_upd,
        message=f"Importazione completata: {f_ins + m_ins} inseriti, {f_upd + m_upd} aggiornati.",
    )
