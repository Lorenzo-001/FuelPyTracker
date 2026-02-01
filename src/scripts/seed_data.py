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
    start_date = date(2022, 1, 1) # Partiamo un po' più recenti
    current_km = 45000            
    base_price = 1.650            
    
    last_service_km = current_km  
    last_tires_km = current_km    
    last_tax_year = start_date.year - 1 
    
    print("🚀 Generazione eventi...")
    
    fuel_count = 0
    maint_count = 0
    curr_date = start_date
    
    while curr_date < date.today():
        # --- AVANZAMENTO TEMPO E KM ---
        days_skip = random.randint(7, 20) # Frequenza rifornimenti realistica
        curr_date += timedelta(days=days_skip)
        
        if curr_date > date.today():
            break

        km_driven = days_skip * random.randint(40, 70) 
        current_km += km_driven
        
        # --- A. MANUTENZIONE ---
        
        # 1. TAGLIANDO (Scadenza KM)
        if (current_km - last_service_km) >= random.randint(19000, 21000):
            next_expiry = current_km + 20000 # Prossimo tagliando tra 20k km
            
            crud.create_maintenance(
                db, user_id,
                curr_date, 
                current_km, 
                "Tagliando", 
                random.uniform(250.0, 400.0), 
                f"Tagliando ordinario {current_km}km (Olio, Filtri)",
                expiry_km=next_expiry, # [NEW] Imposta scadenza futura
                expiry_date=None
            )
            last_service_km = current_km
            maint_count += 1
            print(f"   [🔧] Tagliando a {current_km} km (Prossimo a {next_expiry})")

        # 2. GOMME (Scadenza KM)
        if (current_km - last_tires_km) >= random.randint(40000, 50000):
            next_expiry = current_km + 45000
            
            crud.create_maintenance(
                db, user_id,
                curr_date, 
                current_km, 
                "Gomme", 
                random.uniform(400.0, 650.0), 
                "Sostituzione treno gomme 4 stagioni",
                expiry_km=next_expiry, # [NEW]
                expiry_date=None
            )
            last_tires_km = current_km
            maint_count += 1
            print(f"   [🛞] Cambio Gomme a {current_km} km")

        # 3. BOLLO (Scadenza DATA)
        if curr_date.year > last_tax_year and curr_date.month >= 2:
            # Scade l'anno prossimo stesso mese
            next_expiry_date = date(curr_date.year + 1, 1, 31) 
            
            crud.create_maintenance(
                db, user_id,
                curr_date, 
                current_km, 
                "Bollo", 
                215.00, 
                f"Tassa di proprietà anno {curr_date.year}",
                expiry_km=None,
                expiry_date=next_expiry_date # [NEW] Imposta scadenza data
            )
            last_tax_year = curr_date.year
            maint_count += 1
            print(f"   [📄] Bollo pagato (Scadenza {next_expiry_date})")

        # 4. REVISIONE (Scadenza DATA - Ogni 2 anni)
        # Semplificazione: facciamo finta scada negli anni pari
        if curr_date.year % 2 == 0 and curr_date.month == 6 and curr_date.day < 15:
             next_expiry_date = date(curr_date.year + 2, 6, 30)
             
             crud.create_maintenance(
                db, user_id,
                curr_date,
                current_km,
                "Revisione",
                79.00,
                "Revisione Ministeriale",
                expiry_km=None,
                expiry_date=next_expiry_date # [NEW]
             )
             maint_count += 1
             print(f"   [📋] Revisione effettuata (Scadenza {next_expiry_date})")

        # 5. GUASTO CASUALE (Nessuna scadenza)
        if random.random() < 0.02:
             types = [("Batteria", 120.0), ("Riparazione", 150.0)]
             m_type, m_cost = random.choice(types)
             crud.create_maintenance(
                db, user_id,
                curr_date, 
                current_km, 
                m_type, 
                m_cost, 
                "Intervento imprevisto",
                expiry_km=None, # Nessuna scadenza per guasti
                expiry_date=None
            )
             maint_count += 1

        # --- B. RIFORNIMENTO ---
        price_fluctuation = random.uniform(-0.10, 0.10)
        trend = (fuel_count * 0.003) 
        current_price = base_price + price_fluctuation + trend
        
        base_eff = 16.0 - (current_km / 300000)
        efficiency = random.uniform(base_eff - 1, base_eff + 1)
        
        liters_needed = km_driven / efficiency
        total_cost = liters_needed * current_price
        is_full = random.random() > 0.15
        
        crud.create_refueling(
            db, user_id,
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
    print("--- FUELPYTRACKER SEEDER v2 (Predictive Ready) ---")
    target_uuid = input("Inserisci il tuo User ID (UUID) copiandolo da Supabase: ").strip()
    
    if len(target_uuid) < 10:
        print("❌ UUID non valido.")
    else:
        seed(target_uuid)