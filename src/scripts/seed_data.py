import sys
import os
import random
from datetime import date, timedelta

# Fix Path per vedere i moduli src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.core import init_db, SessionLocal
from database import crud

def seed():
    print("🌱 Inizio popolamento database...")
    
    # 1. Ricrea DB pulito
    db = SessionLocal()
    init_db() # Assicurati che il vecchio file .db sia stato cancellato se vuoi ripartire da zero
    
    # 2. Configurazione Generatore
    start_date = date(2022, 1, 1)
    current_km = 50000
    base_price = 1.650
    
    print("Generazione rifornimenti dal 2022 a oggi...")
    
    records_count = 0
    curr_date = start_date
    
    while curr_date < date.today():
        # Avanza di 10-20 giorni
        days_skip = random.randint(10, 20)
        curr_date += timedelta(days=days_skip)
        
        if curr_date > date.today():
            break

        # Simula Km percorsi (es. 40-60 km al giorno)
        km_driven = days_skip * random.randint(40, 60)
        current_km += km_driven
        
        # Simula oscillazione prezzo (+/- 5 centesimi casuali)
        price_fluctuation = random.uniform(-0.05, 0.05)
        # Trend generale in aumento leggero nel tempo
        trend = (records_count * 0.002) 
        current_price = base_price + price_fluctuation + trend
        
        # Simula Litri necessari (Consumo medio ~15 km/l + rumore)
        efficiency = random.uniform(14.0, 16.0)
        liters_needed = km_driven / efficiency
        
        # Calcola costo
        total_cost = liters_needed * current_price
        
        # Ogni tanto (10%) simula un parziale
        is_full = random.random() > 0.1
        
        crud.create_refueling(
            db=db,
            date_obj=curr_date,
            total_km=current_km,
            price_per_liter=round(current_price, 3),
            total_cost=round(total_cost, 2),
            liters=round(liters_needed, 2),
            is_full_tank=is_full,
            notes="Dato fittizio generato da script"
        )
        records_count += 1

    print(f"✅ Inseriti {records_count} rifornimenti.")
    db.close()

if __name__ == "__main__":
    seed()