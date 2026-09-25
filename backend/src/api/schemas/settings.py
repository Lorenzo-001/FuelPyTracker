"""
Modelli Pydantic per il dominio Configurazioni & Impostazioni Utente (/api/settings).
Definisce le strutture per i parametri di sicurezza, soglie allerta, limiti import e categorie personalizzate.
"""
from __future__ import annotations

from typing import List, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field


class AppSettingsResponse(BaseModel):
    """Configurazione completa delle preferenze e delle soglie utente."""
    price_fluctuation_cents: float = Field(..., description="Margine di tolleranza oscillazione prezzo carburante (+/- €)")
    max_total_cost: float = Field(..., description="Tetto massimo di sicurezza per singolo rifornimento (€)")
    max_accumulated_partial_cost: float = Field(..., description="Soglia di allarme per accumulo spesa rifornimenti parziali (€)")
    reminder_types: List[str] = Field(default_factory=list, description="Categorie selezionabili per i promemoria periodici")
    maintenance_types: List[str] = Field(default_factory=list, description="Tipologie di spesa selezionabili per le manutenzioni")
    import_kml_min: float = Field(..., description="Consumo minimo plausibile in Km/L (soglia warning importazione)")
    import_kml_max: float = Field(..., description="Consumo massimo plausibile in Km/L (soglia warning importazione)")
    import_kml_error: float = Field(..., description="Consumo fisicamente impossibile in Km/L (soglia errore bloccante)")
    import_kmd_max: float = Field(..., description="Distanza massima percorribile in un giorno in km/giorno (errore bloccante)")
    ocr_add_station_to_notes: bool = Field(True, description="Inserisce automaticamente il nome del distributore nelle note")
    ocr_add_liters_to_notes: bool = Field(True, description="Inserisce automaticamente il dettaglio litri erogati nelle note")
    vehicle_name: Optional[str] = Field("Il mio Veicolo", description="Nome o modello del veicolo monitorato")
    vehicle_plate: Optional[str] = Field("", description="Targa del veicolo")
    vehicle_fuel_type: Optional[str] = Field("Benzina", description="Tipologia alimentazione (Benzina, Diesel, GPL, Metano, Ibrida, Elettrica)")

    model_config = {"from_attributes": True}


class AppSettingsUpdate(BaseModel):
    """Payload per l'aggiornamento parziale o completo delle impostazioni utente."""
    price_fluctuation_cents: Optional[float] = Field(None, gt=0, le=1.0)
    max_total_cost: Optional[float] = Field(None, gt=0)
    max_accumulated_partial_cost: Optional[float] = Field(None, gt=0)
    reminder_types: Optional[List[str]] = None
    maintenance_types: Optional[List[str]] = None
    import_kml_min: Optional[float] = Field(None, gt=0)
    import_kml_max: Optional[float] = Field(None, gt=0)
    import_kml_error: Optional[float] = Field(None, gt=0)
    import_kmd_max: Optional[float] = Field(None, gt=0)
    ocr_add_station_to_notes: Optional[bool] = None
    ocr_add_liters_to_notes: Optional[bool] = None
    vehicle_name: Optional[str] = Field(None, max_length=100)
    vehicle_plate: Optional[str] = Field(None, max_length=20)
    vehicle_fuel_type: Optional[str] = Field(None, max_length=50)


class CategoryOperationRequest(BaseModel):
    """Payload per l'aggiunta o rimozione di una voce di categoria."""
    category: str = Field(..., min_length=1, max_length=100, description="Nome della categoria da aggiungere o rimuovere")
