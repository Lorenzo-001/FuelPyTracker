from datetime import date
from src.database.models import Refueling
from src.services.business.calculations import calculate_stats

def test_simple_consumption():
    """Scenario Standard: Due pieni completi consecutivi."""
    # 1. Setup dati (Prev: 1000km, Curr: 1800km, Litri immessi: 40)
    prev = Refueling(id=1, date=date(2025, 1, 1), total_km=1000, liters=50, is_full_tank=True)
    curr = Refueling(id=2, date=date(2025, 1, 15), total_km=1800, liters=40, is_full_tank=True)
    
    # 2. Esecuzione calcolo
    stats = calculate_stats(curr, [curr, prev])
    
    # 3. Verifica: Delta=800km, Consumo=20km/l (800/40)
    assert stats["delta_km"] == 800
    assert stats["km_per_liter"] == 20.0

def test_partial_refueling_logic():
    """Scenario Complesso: Pieno -> Parziale -> Pieno."""
    # 1. Setup: Pieno A (1000km) -> Parziale (10L) -> Pieno B (1500km, 30L)
    r1 = Refueling(id=1, date=date(2025, 1, 1), total_km=1000, is_full_tank=True)
    r2 = Refueling(id=2, date=date(2025, 1, 5), total_km=1200, liters=10, is_full_tank=False)
    r3 = Refueling(id=3, date=date(2025, 1, 10), total_km=1500, liters=30, is_full_tank=True)
    
    # Lista ordinata decrescente come da query DB reale
    history = [r3, r2, r1] 
    
    # 2. Esecuzione su r3 (Pieno finale)
    stats = calculate_stats(r3, history)
    
    # 3. Verifica
    # Delta Km: 1500 - 1200 = 300 (rispetto all'ultimo record fisico)
    assert stats["delta_km"] == 300
    # Consumo: (1500 - 1000) / (10 + 30) = 500 / 40 = 12.5 km/l
    assert stats["km_per_liter"] == 12.5

def test_first_record():
    """Edge Case: Primo inserimento assoluto (nessun storico)."""
    curr = Refueling(id=1, date=date(2025, 1, 1), total_km=1000, is_full_tank=True)
    
    stats = calculate_stats(curr, [curr])
    
    assert stats["delta_km"] == 0
    assert stats["km_per_liter"] is None