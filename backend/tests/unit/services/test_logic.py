from datetime import date
from src.database.models import Refueling
from src.services.business.calculations import calculate_stats

def test_simple_consumption():
    """Caso base: due pieni completi consecutivi."""
    prev = Refueling(id=1, date=date(2025, 1, 1), total_km=1000, liters=50, is_full_tank=True)
    curr = Refueling(id=2, date=date(2025, 1, 15), total_km=1800, liters=40, is_full_tank=True)
    
    # Km fatti: 800. Litri messi: 40. Risultato atteso: 20 km/l
    stats = calculate_stats(curr, [curr, prev])
    
    assert stats["delta_km"] == 800
    assert stats["km_per_liter"] == 20.0

def test_partial_refueling_logic():
    """Caso complesso: Pieno -> Parziale -> Pieno."""
    # 1. Pieno Iniziale
    r1 = Refueling(id=1, date=date(2025, 1, 1), total_km=1000, is_full_tank=True)
    
    # 2. Parziale (non si può calcolare consumo qui)
    r2 = Refueling(id=2, date=date(2025, 1, 5), total_km=1200, liters=10, is_full_tank=False)
    
    # 3. Pieno Finale
    # Distanza totale da r1: 1500 - 1000 = 500 km
    # Litri totali usati: 10 (del parziale) + 30 (di ora) = 40 litri
    # Consumo atteso: 500 / 40 = 12.5 km/l
    r3 = Refueling(id=3, date=date(2025, 1, 10), total_km=1500, liters=30, is_full_tank=True)
    
    history = [r3, r2, r1] # Ordine decrescente
    
    stats = calculate_stats(r3, history)
    
    assert stats["delta_km"] == 300  # Rispetto a r2
    assert stats["km_per_liter"] == 12.5

def test_first_record():
    """Primo record assoluto: niente calcoli."""
    curr = Refueling(id=1, date=date(2025, 1, 1), total_km=1000, is_full_tank=True)
    stats = calculate_stats(curr, [curr])
    
    assert stats["delta_km"] == 0
    assert stats["km_per_liter"] is None