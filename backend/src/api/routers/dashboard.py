"""
Router API per il dominio Dashboard & Analytics (/api/dashboard).
Fornisce KPI aggregati, Car Health Score, serie per grafici e simulatore Trip Calculator.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional, List, Dict
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Query
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from src.database import crud
from src.api.deps import get_db, get_current_user_id
from src.api.schemas.dashboard import (
    LastRefuelingSummary,
    HealthScoreSummary,
    PartialAccumulationAlert,
    DashboardSummaryResponse,
    PriceTrendPoint,
    EfficiencyPoint,
    MonthlySpendingPoint,
    DashboardChartsResponse,
    TripCalculatorRequest,
    TripCalculatorResponse,
)
from src.services.business import gamification
from src.services.business.calculations import calculate_stats, check_partial_accumulation

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

MONTH_NAMES_IT = {
    1: "Gen", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mag", 6: "Giu",
    7: "Lug", 8: "Ago", 9: "Set", 10: "Ott", 11: "Nov", 12: "Dic"
}


def _get_cutoff_date(time_range: str) -> Optional[date]:
    """Calcola la data di inizio intervallo in base all'opzione temporale."""
    today = date.today()
    if time_range == "1m":
        return today - timedelta(days=30)
    elif time_range == "3m":
        return today - timedelta(days=90)
    elif time_range == "6m":
        return today - timedelta(days=180)
    elif time_range == "ytd":
        return date(today.year, 1, 1)
    elif time_range == "1y":
        return today - timedelta(days=365)
    elif time_range == "3y":
        return today - timedelta(days=365 * 3)
    return None


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    summary="Cruscotto KPI aggregati e Car Health Score",
    description="Restituisce la panoramica completa con spesa complessiva, ultimo rifornimento, salute auto e allarmi parziali, filtrabile per orizzonte temporale.",
)
def get_dashboard_summary(
    time_range: str = Query("all", pattern="^(1m|3m|6m|ytd|1y|3y|all)$", description="Intervallo temporale per il calcolo di spese e consumi (1m, 3m, 6m, ytd, 1y, 3y, all)"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> DashboardSummaryResponse:
    refuelings = crud.get_all_refuelings(db, user_id)
    maintenances = crud.get_all_maintenances(db, user_id)
    settings = crud.get_settings(db, user_id)

    current_km = max((r.total_km for r in refuelings), default=0)

    # 1. Ultimo Rifornimento (stato globale veicolo)
    last_refuel = max(refuelings, key=lambda x: x.date, default=None)
    last_dto = None
    if last_refuel:
        last_dto = LastRefuelingSummary(
            date=last_refuel.date,
            total_cost=last_refuel.total_cost,
            price_per_liter=last_refuel.price_per_liter,
            liters=last_refuel.liters,
        )

    # 2. Car Health Score (stato attuale veicolo)
    health_score, issues = gamification.calculate_car_health_score(db, user_id, current_km)
    status_color = "green" if health_score >= 80 else ("orange" if health_score >= 50 else "red")
    health_dto = HealthScoreSummary(
        score=health_score,
        status_color=status_color,
        issues=issues,
    )

    # 3. Alert Parziali (stato attuale veicolo)
    partial_info = check_partial_accumulation(refuelings)
    max_threshold = settings.max_accumulated_partial_cost if settings else 150.0
    partial_alert = PartialAccumulationAlert(
        accumulated_cost=round(partial_info["accumulated_cost"], 2),
        partials_count=partial_info["partials_count"],
        is_warning=partial_info["accumulated_cost"] > max_threshold,
        max_threshold=max_threshold,
    )

    # 4. Spesa e Consumi nel periodo selezionato
    cutoff = _get_cutoff_date(time_range)
    f_refuelings = [r for r in refuelings if cutoff is None or r.date >= cutoff]
    f_maintenances = [m for m in maintenances if cutoff is None or m.date >= cutoff]

    total_fuel_cost = round(sum(r.total_cost for r in f_refuelings), 2)
    total_maint_cost = round(sum(m.cost for m in f_maintenances), 2)
    total_spent = round(total_fuel_cost + total_maint_cost, 2)

    valid_eff = [
        s["km_per_liter"]
        for r in f_refuelings
        if (s := calculate_stats(r, refuelings)).get("km_per_liter") is not None
    ]
    avg_kml = round(sum(valid_eff) / len(valid_eff), 2) if valid_eff else 0.0

    return DashboardSummaryResponse(
        current_km=current_km,
        last_refueling=last_dto,
        health_score=health_dto,
        partial_alert=partial_alert,
        total_fuel_cost=total_fuel_cost,
        total_maintenance_cost=total_maint_cost,
        total_spent=total_spent,
        avg_km_per_liter=avg_kml,
    )


@router.get(
    "/charts",
    response_model=DashboardChartsResponse,
    summary="Serie temporali per grafici analitici",
    description="Fornisce i punti per i grafici Prezzo Carburante, Efficienza Km/L e Spesa Mensile, filtrati per intervallo temporale.",
)
def get_dashboard_charts(
    time_range: str = Query("all", pattern="^(1m|3m|6m|ytd|1y|3y|all)$", description="Intervallo temporale (1m, 3m, 6m, ytd, 1y, 3y, all)"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> DashboardChartsResponse:
    refuelings = crud.get_all_refuelings(db, user_id)
    maintenances = crud.get_all_maintenances(db, user_id)
    cutoff = _get_cutoff_date(time_range)

    # Filtro temporale
    f_refuelings = [r for r in refuelings if cutoff is None or r.date >= cutoff]
    f_maintenances = [m for m in maintenances if cutoff is None or m.date >= cutoff]

    # 1. Price Trend
    sorted_refs = sorted(f_refuelings, key=lambda x: x.date)
    price_points = [
        PriceTrendPoint(date=r.date, price_per_liter=r.price_per_liter)
        for r in sorted_refs
    ]

    # 2. Efficiency Trend (Full-to-Full calcolato rispetto allo storico completo)
    eff_points = []
    for r in sorted_refs:
        stats = calculate_stats(r, refuelings)
        kml = stats.get("km_per_liter")
        if kml is not None:
            eff_points.append(EfficiencyPoint(date=r.date, km_per_liter=round(kml, 2)))

    # 3. Monthly Spending (Raggruppamento per Anno-Mese)
    monthly_data: Dict[str, Dict[str, float]] = {}

    for r in f_refuelings:
        key = f"{r.date.year:04d}-{r.date.month:02d}"
        if key not in monthly_data:
            monthly_data[key] = {"fuel": 0.0, "maint": 0.0}
        monthly_data[key]["fuel"] += r.total_cost

    for m in f_maintenances:
        key = f"{m.date.year:04d}-{m.date.month:02d}"
        if key not in monthly_data:
            monthly_data[key] = {"fuel": 0.0, "maint": 0.0}
        monthly_data[key]["maint"] += m.cost

    spending_points = []
    for key in sorted(monthly_data.keys()):
        year, month = map(int, key.split("-"))
        m_label = f"{MONTH_NAMES_IT.get(month, str(month))} {str(year)[2:]}"
        fuel = round(monthly_data[key]["fuel"], 2)
        maint = round(monthly_data[key]["maint"], 2)
        spending_points.append(
            MonthlySpendingPoint(
                month=key,
                label=m_label,
                fuel_cost=fuel,
                maintenance_cost=maint,
                total_cost=round(fuel + maint, 2),
            )
        )

    return DashboardChartsResponse(
        price_trend=price_points,
        efficiency=eff_points,
        monthly_spending=spending_points,
    )


@router.post(
    "/trip-calculator",
    response_model=TripCalculatorResponse,
    summary="Simulatore preventivo costo viaggio",
    description="Stima carburante e spesa necessari per un tragitto basandosi su consumi e prezzi storici o custom.",
)
def calculate_trip(
    payload: TripCalculatorRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> TripCalculatorResponse:
    refuelings = crud.get_all_refuelings(db, user_id)

    # Risoluzione Efficienza (Km/L)
    if payload.avg_kml is not None:
        calc_kml = payload.avg_kml
    else:
        valid_eff = [
            s["km_per_liter"]
            for r in refuelings
            if (s := calculate_stats(r, refuelings)).get("km_per_liter") is not None
        ]
        calc_kml = (sum(valid_eff) / len(valid_eff)) if valid_eff else 15.0

    # Risoluzione Prezzo (€/L)
    if payload.fuel_price is not None:
        calc_price = payload.fuel_price
    else:
        last_refuel = max(refuelings, key=lambda x: x.date, default=None)
        calc_price = last_refuel.price_per_liter if last_refuel else 1.80

    liters_needed = round(payload.trip_km / calc_kml, 2)
    estimated_cost = round(liters_needed * calc_price, 2)
    cost_per_km = round(estimated_cost / payload.trip_km, 3)

    return TripCalculatorResponse(
        trip_km=payload.trip_km,
        avg_kml=round(calc_kml, 2),
        fuel_price=round(calc_price, 3),
        liters_needed=liters_needed,
        estimated_cost=estimated_cost,
        cost_per_km=cost_per_km,
    )
