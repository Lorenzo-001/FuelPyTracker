import sys
import os
import random
from datetime import date, timedelta

# Comando Avvio: python -m src.scripts.seed_data

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)

from src.database.core import init_db, SessionLocal
from src.database import crud
from src.database.models import Refueling, Maintenance

def clean_database(db, user_id):
    """Svuota i dati SOLO dell'utente corrente."""
    print(f"🧹 Pulizia dati per l'utente {user_id}...")
    try:
        # Cancelliamo filtrando per user_id per non toccare altri utenti
        db.query(Maintenance).filter(Maintenance.user_id == user_id).delete()
        db.query(Refueling).filter(Refueling.user_id == user_id).delete()
        db.commit()
        print("✅ Dati utente rimossi.")
    except Exception as e:
        print(f"⚠️ Errore pulizia: {e}")
        db.rollback()

def seed(user_id):
    print(f"🌱 Inizio popolamento database per UserID: {user_id}")
    
    try:
        init_db() 
        db = SessionLocal()
    except Exception as e:
        print(f"❌ Errore connessione DB: {e}")
        return

    # Pulizia mirata
    clean_database(db, user_id)
    
    # Configurazione simulazione
    start_date = date(2020, 1, 1) 
    current_km = 45000            
    base_price = 1.450            
    
    last_service_km = current_km  
    last_tires_km = current_km    
    last_tax_year = start_date.year - 1 
    
    print("🚀 Generazione eventi dal 2020 a oggi...")
    
    fuel_count = 0
    maint_count = 0
    curr_date = start_date
    
    while curr_date < date.today():
        # --- AVANZAMENTO TEMPO E KM ---
        days_skip = random.randint(10, 25)
        curr_date += timedelta(days=days_skip)
        
        if curr_date > date.today():
            break

        km_driven = days_skip * random.randint(35, 65) 
        current_km += km_driven
        
        # --- A. MANUTENZIONE ---
        
        # 1. TAGLIANDO
        if (current_km - last_service_km) >= random.randint(19000, 21000):
            crud.create_maintenance(
                db, user_id, # <--- PASSAGGIO USER ID
                curr_date, 
                current_km, 
                "Tagliando", 
                random.uniform(220.0, 350.0), 
                f"Tagliando ordinario {current_km}km (Olio, Filtri)"
            )
            last_service_km = current_km
            maint_count += 1
            print(f"   [🔧] Tagliando a {current_km} km")

        # 2. GOMME
        if (current_km - last_tires_km) >= random.randint(42000, 48000):
            crud.create_maintenance(
                db, user_id, # <--- PASSAGGIO USER ID
                curr_date, 
                current_km, 
                "Gomme", 
                random.uniform(380.0, 600.0), 
                "Sostituzione treno gomme 4 stagioni"
            )
            last_tires_km = current_km
            maint_count += 1
            print(f"   [🛞] Cambio Gomme a {current_km} km")

        # 3. BOLLO
        if curr_date.year > last_tax_year and curr_date.month >= 2:
            crud.create_maintenance(
                db, user_id, # <--- PASSAGGIO USER ID
                curr_date, 
                current_km, 
                "Bollo", 
                215.00, 
                f"Tassa di proprietà anno {curr_date.year}"
            )
            last_tax_year = curr_date.year
            maint_count += 1
            print(f"   [📄] Bollo pagato per il {last_tax_year}")

        # 4. GUASTO CASUALE
        if random.random() < 0.02:
             types = [("Batteria", 120.0), ("Riparazione", 150.0), ("Altro", 50.0)]
             m_type, m_cost = random.choice(types)
             crud.create_maintenance(
                db, user_id, # <--- PASSAGGIO USER ID
                curr_date, 
                current_km, 
                m_type, 
                m_cost, 
                "Intervento imprevisto"
            )
             maint_count += 1

        # --- B. RIFORNIMENTO ---
        
        price_fluctuation = random.uniform(-0.10, 0.10)
        trend = (fuel_count * 0.003) 
        current_price = base_price + price_fluctuation + trend
        
        base_eff = 16.0 - (current_km / 200000)
        efficiency = random.uniform(base_eff - 1, base_eff + 1)
        
        liters_needed = km_driven / efficiency
        total_cost = liters_needed * current_price
        is_full = random.random() > 0.15
        
        crud.create_refueling(
            db, user_id, # <--- PASSAGGIO USER ID
            curr_date, 
            current_km, 
            round(current_price, 3), 
            round(total_cost, 2), 
            round(liters_needed, 2), 
            is_full, 
            "Seed Data"
        )
        fuel_count += 1

    print(f"✅ Completato! Inseriti {fuel_count} rifornimenti e {maint_count} interventi manutenzione.")
    db.close()

if __name__ == "__main__":
    print("--- FUELPYTRACKER SEEDER ---")
    # Richiediamo l'ID all'avvio
    target_uuid = input("Inserisci il tuo User ID (UUID) copiandolo da Supabase: ").strip()
    
    if len(target_uuid) < 10:
        print("❌ UUID non valido. Devi copiare l'ID utente dalla tabella auth.users o dalla Dashboard.")
    else:
        seed(target_uuid)