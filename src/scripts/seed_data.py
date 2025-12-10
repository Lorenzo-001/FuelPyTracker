import sys
import os
import random
from datetime import date, timedelta

# Fix Path per vedere i moduli src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.core import init_db, SessionLocal
from database import crud

def seed():
    print("🌱 Inizio popolamento database (Rifornimenti + Manutenzione)...")
    
    # 1. Ricrea DB pulito
    db = SessionLocal()
    init_db() 
    
    # 2. Configurazione Iniziale
    start_date = date(2020, 1, 1) # Partiamo un po' prima per avere più storico
    current_km = 45000            # Km iniziali dell'auto
    base_price = 1.450            # Prezzo benzina nel 2020
    
    # Variabili di stato per le manutenzioni
    last_service_km = current_km  # Ultimo tagliando
    last_tires_km = current_km    # Ultimo cambio gomme
    last_tax_year = start_date.year - 1 # Ultimo bollo pagato
    
    print("Generazione eventi dal 2020 a oggi...")
    
    fuel_count = 0
    maint_count = 0
    curr_date = start_date
    
    while curr_date < date.today():
        # --- AVANZAMENTO TEMPO E KM ---
        # Avanza di 10-25 giorni casuali
        days_skip = random.randint(10, 25)
        curr_date += timedelta(days=days_skip)
        
        if curr_date > date.today():
            break

        # Simula Km percorsi in questo intervallo
        km_driven = days_skip * random.randint(35, 65) # Media 50km/giorno
        current_km += km_driven
        
        # --- A. LOGICA MANUTENZIONE (Check prima del rifornimento) ---
        
        # 1. TAGLIANDO (Ogni 20.000 km +/- 2000 km di variabilità)
        if (current_km - last_service_km) >= random.randint(19000, 21000):
            crud.create_maintenance(
                db=db,
                date_obj=curr_date,
                total_km=current_km,
                expense_type="Tagliando",
                cost=random.uniform(220.0, 350.0),
                description=f"Tagliando ordinario {current_km}km (Olio, Filtri)"
            )
            last_service_km = current_km
            maint_count += 1
            print(f"   [🔧] Tagliando a {current_km} km")

        # 2. GOMME (Ogni 45.000 km +/- 3000 km)
        if (current_km - last_tires_km) >= random.randint(42000, 48000):
            crud.create_maintenance(
                db=db,
                date_obj=curr_date,
                total_km=current_km,
                expense_type="Gomme",
                cost=random.uniform(380.0, 600.0),
                description="Sostituzione treno gomme 4 stagioni"
            )
            last_tires_km = current_km
            maint_count += 1
            print(f"   [🛞] Cambio Gomme a {current_km} km")

        # 3. BOLLO (Una volta l'anno, diciamo a Gennaio/Febbraio)
        if curr_date.year > last_tax_year and curr_date.month >= 2:
            crud.create_maintenance(
                db=db,
                date_obj=curr_date,
                total_km=current_km,
                expense_type="Bollo",
                cost=215.00, # Costo fisso ipotetico
                description=f"Tassa di proprietà anno {curr_date.year}"
            )
            last_tax_year = curr_date.year
            maint_count += 1
            print(f"   [📄] Bollo pagato per il {last_tax_year}")

        # 4. REVISIONE (Ogni 2 anni)
        # Semplificazione: facciamola negli anni pari
        if curr_date.year % 2 == 0 and curr_date.month == 6 and curr_date.day < 15:
             # Controllo per non inserirne 2 nello stesso mese
             # (la logica del loop potrebbe passare più volte in giugno)
             # Ma essendo un seed veloce, accettiamo il rischio o usiamo un flag.
             # Per semplicità qui simuliamo un evento raro casuale.
             pass 

        # 5. GUASTO CASUALE (Molto raro: 2% probabilità ad ogni ciclo)
        if random.random() < 0.02:
             types = [("Batteria", 120.0), ("Riparazione", 150.0), ("Altro", 50.0)]
             m_type, m_cost = random.choice(types)
             crud.create_maintenance(
                db=db,
                date_obj=curr_date,
                total_km=current_km,
                expense_type=m_type,
                cost=m_cost,
                description="Intervento imprevisto"
            )
             maint_count += 1

        # --- B. LOGICA RIFORNIMENTO ---
        
        # Oscillazione prezzo (+/- 10 centesimi) e trend inflazione
        price_fluctuation = random.uniform(-0.10, 0.10)
        trend = (fuel_count * 0.003) 
        current_price = base_price + price_fluctuation + trend
        
        # Efficienza (Km/L) che peggiora leggermente con l'invecchiamento auto
        base_eff = 16.0 - (current_km / 200000) # Perde 1 km/l ogni 200k km
        efficiency = random.uniform(base_eff - 1, base_eff + 1)
        
        liters_needed = km_driven / efficiency
        total_cost = liters_needed * current_price
        
        # Simulazione parziali (15% dei casi)
        is_full = random.random() > 0.15
        
        crud.create_refueling(
            db=db,
            date_obj=curr_date,
            total_km=current_km,
            price_per_liter=round(current_price, 3),
            total_cost=round(total_cost, 2),
            liters=round(liters_needed, 2),
            is_full_tank=is_full,
            notes="Seed Data"
        )
        fuel_count += 1

    print(f"✅ Completato! Inseriti {fuel_count} rifornimenti e {maint_count} interventi manutenzione.")
    db.close()

if __name__ == "__main__":
    seed()