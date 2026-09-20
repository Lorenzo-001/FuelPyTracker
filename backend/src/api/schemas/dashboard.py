"""
Modelli Pydantic per il dominio Dashboard & Analytics (/api/dashboard).
Definisce le strutture per i KPI aggregati, Car Health Score, serie per grafici e Trip Calculator.
"""
from __future__ import annotations

import datetime as dt
from typing import List, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


class LastRefuelingSummary(BaseModel):
    """Sintesi essenziale dell'ultimo rifornimento registrato."""
    date: Optional[dt.date] = None
    total_cost: Optional[float] = None
    price_per_liter: Optional[float] = None
    liters: Optional[float] = None


class HealthScoreSummary(BaseModel):
    """Stato di salute del veicolo calcolato dall'algoritmo di gamification."""
    score: int = Field(100, description="Punteggio di salute del veicolo normalizzato da 0 a 100")
    status_color: str = Field("green", description="Codice colore UI: 'green' (>=80), 'orange' (50-79), 'red' (<50)")
    issues: List[str] = Field(default_factory=list, description="Lista degli elementi scaduti o controlli non rispettati")


class PartialAccumulationAlert(BaseModel):
    """Monitoraggio dell'accumulo di spesa per rifornimenti parziali non consolidati da un pieno."""
    accumulated_cost: float = Field(0.0, description="Spesa totale accumulata dall'ultimo pieno")
    partials_count: int = Field(0, description="Numero di rifornimenti parziali consecutivi")
    is_warning: bool = Field(False, description="True se la spesa supera la soglia di tolleranza impostata")
    max_threshold: float = Field(0.0, description="Soglia limite impostata nelle preferenze utente")


class DashboardSummaryResponse(BaseModel):
    """Cruscotto principale dei KPI e dello stato generale dell'auto."""
    current_km: int = Field(0, description="Ultimo chilometraggio registrato per il veicolo")
    last_refueling: Optional[LastRefuelingSummary] = None
    health_score: HealthScoreSummary
    partial_alert: PartialAccumulationAlert
    total_fuel_cost: float = Field(0.0, description="Spesa totale sostenuta per carburante")
    total_maintenance_cost: float = Field(0.0, description="Spesa totale sostenuta per tagliandi e manutenzioni")
    total_spent: float = Field(0.0, description="Spesa complessiva veicolo (carburante + manutenzioni)")
    avg_km_per_liter: float = Field(0.0, description="Consumo medio storico calcolato con algoritmo Full-to-Full")


class PriceTrendPoint(BaseModel):
    """Punto temporale per il grafico dell'andamento prezzo carburante."""
    date: dt.date
    price_per_liter: float


class EfficiencyPoint(BaseModel):
    """Punto temporale per il grafico dell'efficienza energetica Km/L."""
    date: dt.date
    km_per_liter: float


class MonthlySpendingPoint(BaseModel):
    """Aggregazione mensile della spesa per il grafico a barre comparative."""
    month: str = Field(..., description="Mese di riferimento in formato ISO (YYYY-MM)")
    label: str = Field(..., description="Etichetta leggibile del mese (es. 'Mag 25')")
    fuel_cost: float = Field(0.0, description="Spesa carburante sostenuta nel mese")
    maintenance_cost: float = Field(0.0, description="Spesa manutenzione sostenuta nel mese")
    total_cost: float = Field(0.0, description="Spesa totale nel mese")


class DashboardChartsResponse(BaseModel):
    """Contenitore per le serie temporali destinate ai grafici del frontend."""
    price_trend: List[PriceTrendPoint] = Field(default_factory=list)
    efficiency: List[EfficiencyPoint] = Field(default_factory=list)
    monthly_spending: List[MonthlySpendingPoint] = Field(default_factory=list)


class TripCalculatorRequest(BaseModel):
    """Parametri per la simulazione e preventivazione del costo di un viaggio."""
    trip_km: float = Field(..., gt=0, description="Lunghezza del viaggio programmato in chilometri")
    avg_kml: Optional[float] = Field(None, gt=0, description="Efficienza Km/L stimata (default: media storica dell'utente)")
    fuel_price: Optional[float] = Field(None, gt=0, description="Prezzo al litro stimato (default: ultimo prezzo pagato)")


class TripCalculatorResponse(BaseModel):
    """Risultato del calcolo preventivo del costo di viaggio."""
    trip_km: float
    avg_kml: float
    fuel_price: float
    liters_needed: float = Field(..., description="Quantità stimata di carburante necessaria in litri")
    estimated_cost: float = Field(..., description="Costo stimato totale del viaggio in Euro")
    cost_per_km: float = Field(..., description="Costo unitario stimato per chilometro in Euro/Km")
