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
# MODIFICA: Importati i nuovi modelli
from src.database.models import Refueling, Maintenance, Reminder, ReminderHistory, AppSettings 

def clean_database(db, user_id):
    """Svuota i dati SOLO dell'utente corrente."""
    print(f"🧹 Pulizia dati per l'utente {user_id}...")
    try:
        # Cancelliamo filtrando per user_id per non toccare altri utenti
        # Ordine importante per chiavi esterne (History -> Reminder)
        db.query(ReminderHistory).filter(ReminderHistory.user_id == user_id).delete()
        db.query(Reminder).filter(Reminder.user_id == user_id).delete()
        
        db.query(Maintenance).filter(Maintenance.user_id == user_id).delete()
        db.query(Refueling).filter(Refueling.user_id == user_id).delete()
        
        # Opzionale: Resetta settings o lasciali
        db.query(AppSettings).filter(AppSettings.user_id == user_id).delete()
        
        db.commit()
        print("✅ Dati utente rimossi.")
    except Exception as e:
        print(f"⚠️ Errore pulizia: {e}")
        db.rollback()

def _disable_previous_expiry(db, record_id):
    """Rimuove la scadenza da un record precedente per evitare duplicati."""
    if record_id:
        db.query(Maintenance).filter(Maintenance.id == record_id).update({
            "expiry_km": None,
            "expiry_date": None
        })
        db.commit()

def seed(user_id):
    print(f"🌱 Inizio popolamento database per UserID: {user_id}")
    
    try:
        init_db()  # Questo creerà le nuove tabelle se non esistono!
        db = SessionLocal()
    except Exception as e:
        print(f"❌ Errore connessione DB: {e}")
        return

    # Pulizia mirata
    clean_database(db, user_id)
    
    # 1. SETUP IMPOSTAZIONI (Con categorie custom)
    print("⚙️ Configurazione Settings...")
    custom_labels = ["Controllo Livello Olio", "Pressione Pneumatici", "Liquido Lavavetri", "Pulizia Interni"]
    crud.update_settings(db, user_id, 0.15, 120.0, 80.0, custom_labels)

    # Configurazione simulazione
    start_date = date(2022, 1, 1) 
    current_km = 45000            
    base_price = 1.650            
    
    last_service_km = current_km  
    last_tires_km = current_km    
    last_tax_year = start_date.year - 1 
    
    # Tracciamento degli ultimi ID inseriti per gestire le scadenze
    last_active_ids = {
        "Tagliando": None,
        "Gomme": None,
        "Bollo": None,
        "Revisione": None
    }

    print("🚀 Generazione eventi...")
    
    fuel_count = 0
    maint_count = 0
    curr_date = start_date
    
    while curr_date < date.today():
        # --- AVANZAMENTO TEMPO E KM ---
        days_skip = random.randint(7, 20)
        curr_date += timedelta(days=days_skip)
        
        if curr_date > date.today():
            break

        km_driven = days_skip * random.randint(40, 70) 
        current_km += km_driven
        
        # --- A. MANUTENZIONE (Logica Esistente) ---
        
        # 1. TAGLIANDO
        if (current_km - last_service_km) >= random.randint(19000, 21000):
            _disable_previous_expiry(db, last_active_ids["Tagliando"])
            next_expiry = current_km + 20000 
            new_rec = crud.create_maintenance(
                db, user_id, curr_date, current_km, "Tagliando", 
                random.uniform(250.0, 400.0), f"Tagliando ordinario",
                expiry_km=next_expiry, expiry_date=None
            )
            last_active_ids["Tagliando"] = new_rec.id
            last_service_km = current_km
            maint_count += 1

        # 2. GOMME
        if (current_km - last_tires_km) >= random.randint(40000, 50000):
            _disable_previous_expiry(db, last_active_ids["Gomme"])
            next_expiry = current_km + 45000
            new_rec = crud.create_maintenance(
                db, user_id, curr_date, current_km, "Gomme", 
                random.uniform(400.0, 650.0), "Sostituzione gomme",
                expiry_km=next_expiry, expiry_date=None
            )
            last_active_ids["Gomme"] = new_rec.id
            last_tires_km = current_km
            maint_count += 1

        # 3. BOLLO
        if curr_date.year > last_tax_year and curr_date.month >= 2:
            _disable_previous_expiry(db, last_active_ids["Bollo"])
            next_expiry_date = date(curr_date.year + 1, 1, 31) 
            new_rec = crud.create_maintenance(
                db, user_id, curr_date, current_km, "Bollo", 
                215.00, f"Bollo {curr_date.year}",
                expiry_km=None, expiry_date=next_expiry_date 
            )
            last_active_ids["Bollo"] = new_rec.id
            last_tax_year = curr_date.year
            maint_count += 1

        # 4. REVISIONE
        if curr_date.year % 2 == 0 and curr_date.month == 6 and curr_date.day < 15:
             _disable_previous_expiry(db, last_active_ids["Revisione"])
             next_expiry_date = date(curr_date.year + 2, 6, 30)
             new_rec = crud.create_maintenance(
                db, user_id, curr_date, current_km, "Revisione", 
                79.00, "Revisione", expiry_km=None, expiry_date=next_expiry_date 
             )
             last_active_ids["Revisione"] = new_rec.id
             maint_count += 1

        # 5. GUASTO CASUALE
        if random.random() < 0.02:
             types = [("Batteria", 120.0), ("Riparazione", 150.0)]
             m_type, m_cost = random.choice(types)
             crud.create_maintenance(
                db, user_id, curr_date, current_km, m_type, m_cost, "Intervento imprevisto"
            )
             maint_count += 1

        # --- B. RIFORNIMENTO ---
        price_fluctuation = random.uniform(-0.10, 0.10)
        current_price = base_price + price_fluctuation + (fuel_count * 0.003) 
        efficiency = random.uniform(14.0, 16.0)
        liters_needed = km_driven / efficiency
        total_cost = liters_needed * current_price
        is_full = random.random() > 0.15
        
        crud.create_refueling(
            db, user_id, curr_date, current_km, 
            round(current_price, 3), round(total_cost, 2), 
            round(liters_needed, 2), is_full, "Seed Data"
        )
        fuel_count += 1

    # --- C. GENERAZIONE REMINDERS (Nuova Sezione) ---
    print("🔔 Creazione Reminders...")
    
    # 1. Pressione Pneumatici (Ogni 30 gg) - Attivo
    crud.create_reminder(
        db, user_id, 
        title="Pressione Pneumatici",
        frequency_km=None,
        frequency_days=30,
        current_km=current_km,
        current_date=date.today() - timedelta(days=15), # Fatto 15gg fa (quindi ok)
        notes="Controllare a freddo (2.4 bar)"
    )
    
    # 2. Controllo Olio (Ogni 2000 Km) - In Scadenza!
    # Simuliamo che l'ultimo controllo è stato fatto 2100 km fa -> Deve apparire rosso/giallo
    crud.create_reminder(
        db, user_id, 
        title="Controllo Livello Olio",
        frequency_km=2000,
        frequency_days=None,
        current_km=current_km - 2100, # SCADUTO!
        current_date=date.today() - timedelta(days=60),
        notes="Astecca min/max"
    )

    print(f"✅ Completato! Inseriti {fuel_count} rifornimenti, {maint_count} interventi e 2 Reminders.")
    db.close()

if __name__ == "__main__":
    print("--- FUELPYTRACKER SEEDER v4 (Reminders Ready) ---")
    target_uuid = input("Inserisci il tuo User ID (UUID) copiandolo da Supabase: ").strip()
    
    if len(target_uuid) < 10:
        print("❌ UUID non valido.")
    else:
        seed(target_uuid)