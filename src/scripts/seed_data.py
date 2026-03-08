import sys
import os
import random
import math
from datetime import date, timedelta

# Comando Avvio: python -m src.scripts.seed_data

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
sys.path.append(project_root)

from src.database.core import init_db, SessionLocal
from src.database import crud
from src.database.models import Refueling, Maintenance, Reminder, ReminderHistory, AppSettings

# =============================================================================
# FUELPYTRACKER SEEDER v5 — DATI PSEUDO-REALISTICI
# =============================================================================
# Questo script genera ~3 anni di dati verosimili per un'auto italiana media.
# Profilo veicolo: Volkswagen Golf 2019, benzina, km iniziali 45.000, utente
# mediamente attivo con spostamenti misti città/autostrada.
# =============================================================================

# --- PROFILO PREZZI STORICI CARBURANTE ITALIA (Benzina, €/L) ---
# Fonte: dati MISE/Osservaprezzi approssimati per simulazione
# Ogni entry: (anno, mese, prezzo_base)
PRICE_HISTORY = [
    # 2022: crisi energetica, picco storico estate
    (2022,  1, 1.720), (2022,  2, 1.780), (2022,  3, 2.100),
    (2022,  4, 2.030), (2022,  5, 1.980), (2022,  6, 2.080),
    (2022,  7, 1.990), (2022,  8, 1.930), (2022,  9, 1.810),
    (2022, 10, 1.730), (2022, 11, 1.690), (2022, 12, 1.660),
    # 2023: calo progressivo, taglio accise rinnovato
    (2023,  1, 1.690), (2023,  2, 1.750), (2023,  3, 1.800),
    (2023,  4, 1.830), (2023,  5, 1.820), (2023,  6, 1.850),
    (2023,  7, 1.870), (2023,  8, 1.900), (2023,  9, 1.880),
    (2023, 10, 1.830), (2023, 11, 1.780), (2023, 12, 1.720),
    # 2024: relativa stabilità, leggera risalita estiva
    (2024,  1, 1.720), (2024,  2, 1.740), (2024,  3, 1.770),
    (2024,  4, 1.800), (2024,  5, 1.810), (2024,  6, 1.830),
    (2024,  7, 1.820), (2024,  8, 1.810), (2024,  9, 1.790),
    (2024, 10, 1.760), (2024, 11, 1.730), (2024, 12, 1.710),
    # 2025: inizio anno
    (2025,  1, 1.720), (2025,  2, 1.740), (2025,  3, 1.760),
]

def get_base_price(d: date) -> float:
    """Restituisce il prezzo base mensile più vicino alla data, con interpolazione."""
    best = None
    best_dist = 9999
    for (y, m, p) in PRICE_HISTORY:
        dist = abs((d.year - y) * 12 + (d.month - m))
        if dist < best_dist:
            best_dist = dist
            best = p
    return best if best else 1.750

def get_price_with_noise(d: date) -> float:
    """Prezzo realistico con rumore casuale giornaliero ±0.04 €/L."""
    base = get_base_price(d)
    noise = random.gauss(0, 0.018)  # distribuzione normale, deviazione ±1.8c
    return round(max(1.45, base + noise), 3)

def get_km_per_day(d: date) -> float:
    """KM medi percorsi per giorno, con realistica variazione stagionale."""
    month = d.month
    # Estate (luglio-agosto): più km per vacanze/autostrada
    if month in (7, 8):
        return random.gauss(62, 12)
    # Primavera/Autunno: uso normale
    elif month in (4, 5, 6, 9, 10):
        return random.gauss(51, 10)
    # Inverno: meno km, più traffico, più soste brevi
    else:
        return random.gauss(43, 9)

def get_efficiency(d: date, km_per_day: float) -> float:
    """
    Efficienza realistica (km/L) per benzina.
    Dipende da stagione (freddo = peggio per riscaldamento e batteria) e
    tipo di guida (più autostrada in estate = meglio).
    """
    month = d.month
    if month in (7, 8):
        # Estate: autostrada, condizionatore, efficienza media
        base_eff = random.gauss(14.8, 0.9)
    elif month in (4, 5, 6, 9, 10):
        # Misto: buona efficienza
        base_eff = random.gauss(15.4, 0.8)
    else:
        # Inverno: freddo, riscaldamento, percorsi brevi
        base_eff = random.gauss(13.6, 1.0)
    return max(11.0, min(18.5, base_eff))


# --- STAZIONI CARBURANTE ---
FUEL_STATIONS = [
    "ENI", "IP", "Q8", "Shell", "Tamoil", "Esso", "Agip", "Total", "Api"
]

FUEL_NOTES = [
    "Autostrada A1", "In città", "Vicino ufficio", "Rientro dal weekend",
    "Prima della partenza", "Viaggio di lavoro", "Distributore sotto casa",
    "Dopo il lavaggio auto", "Uscita casello", "Tangenziale",
    "Vicino al supermercato", "Sulla provinciale", "Sosta pranzo",
    "",  # alcune note vuote, realistico
    "", "", ""
]

# --- OFFICINE PER MANUTENZIONE ---
WORKSHOPS = [
    "Autofficina Rossi", "Centro Ford Ufficiale",
    "Meccanico di fiducia Bianchi", "Euromaster", "Speedy",
    "Gommista Ferrari & C.", "Fiat Service Center", "Bosch Car Service"
]

def clean_database(db, user_id):
    """Svuota i dati SOLO dell'utente corrente."""
    print(f"🧹 Pulizia dati per l'utente {user_id}...")
    try:
        db.query(ReminderHistory).filter(ReminderHistory.user_id == user_id).delete()
        db.query(Reminder).filter(Reminder.user_id == user_id).delete()
        db.query(Maintenance).filter(Maintenance.user_id == user_id).delete()
        db.query(Refueling).filter(Refueling.user_id == user_id).delete()
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
    print(f"\n🌱 FUELPYTRACKER SEEDER v5")
    print(f"   UserID target: {user_id}")
    print(f"   Profilo: VW Golf 2019 Benzina, pendolare misto città/autostrada\n")

    try:
        init_db()
        db = SessionLocal()
    except Exception as e:
        print(f"❌ Errore connessione DB: {e}")
        return

    clean_database(db, user_id)

    # =========================================================================
    # 1. SETTINGS
    # =========================================================================
    print("⚙️  Configurazione Settings...")
    custom_labels = [
        "Controllo Livello Olio",
        "Pressione Pneumatici",
        "Liquido Lavavetri",
        "Pulizia Filtro Abitacolo",
        "Verifica Pastiglie Freno"
    ]
    crud.update_settings(db, user_id, 0.12, 140.0, 90.0, custom_labels)

    # =========================================================================
    # 2. CONFIGURAZIONE SIMULAZIONE
    # =========================================================================
    start_date    = date(2022, 1, 5)
    current_km    = 45_200       # Km iniziali realistici per auto 2019
    workshop      = random.choice(WORKSHOPS)

    # KM all'ultimo intervento (inizializzati prima dell'inizio sim)
    last_service_km  = current_km - 3_500   # Tagliando fatto 3.500 km fa
    last_tires_km    = current_km - 12_000  # Gomme cambiate 12.000 km fa
    last_tax_year    = start_date.year - 1  # Bollo pagato l'anno scorso
    last_service_rev_year = start_date.year - 1  # Revisione fatta l'anno scorso

    last_active_ids = {
        "Tagliando":  None,
        "Gomme":      None,
        "Bollo":      None,
        "Revisione":  None,
    }

    # =========================================================================
    # 3. LOOP PRINCIPALE: SIMULAZIONE EVENTI
    # =========================================================================
    print("🚀 Generazione eventi giornalieri...\n")

    fuel_count  = 0
    maint_count = 0
    curr_date   = start_date
    prev_full   = True     # L'ultimo rifornimento era pieno?

    # --- NUOVE VARIABILI E COSTANTI LOGICHE ---
    TANK_CAPACITY = 50.0   # Litri massimi del veicolo in configurazione
    current_fuel_liters = 50.0 # Partiamo col pieno

    # Abitudini Rifornimento
    ROUTINE_STATIONS = random.sample(FUEL_STATIONS, 2)
    last_vacation_year = None
    in_summer_burst = False
    summer_burst_remaining = 0

    while curr_date < date.today():

        # === 3.1 CALCOLO CHILOMETRAGGIO DISPONIBILE (VIRTUAL TANK) ===
        # L'auto può viaggiare solo finché c'è carburante.
        month = curr_date.month
        km_per_day = max(15.0, get_km_per_day(curr_date))
        efficiency = get_efficiency(curr_date, km_per_day)

        # Se non siamo in vacanza simulata, gestiamo il classico drop del serbatoio
        if not in_summer_burst:
            # Scegliamo un livello casuale di "accensione spia riserva" (tra 3L e 12L)
            reserve_trigger = random.uniform(3.0, 12.0)
            liters_to_consume = max(0.0, current_fuel_liters - reserve_trigger)

            # Chilometri che possiamo percorrere prima di fermarci
            km_driven = int(liters_to_consume * efficiency)
            
            # Quanti giorni ci mettiamo a fare questi km?
            days_skip = math.ceil(km_driven / km_per_day)

            # Vacanza Estiva (Luglio-Agosto)? Un solo evento all'anno.
            if month in (7, 8) and curr_date.year != last_vacation_year and random.random() < 0.6:
                in_summer_burst = True
                summer_burst_remaining = random.randint(3, 4)
                last_vacation_year = curr_date.year
                # Accorciamo la prima tratta della vacanza
                days_skip = random.randint(1, 3)
                km_driven = int(days_skip * km_per_day * 4.0) # Giorni densi in autostrada
        else:
            # Durante la vacanza (burst di rifornimenti) guidiamo tanto e ci fermiamo spesso
            days_skip = random.randint(2, 4)
            km_driven = int(days_skip * km_per_day * 4.5)

        curr_date += timedelta(days=days_skip)
        
        # Consumiamo la benzina (anche andando in negativo temporaneamente, se la vacanza è intensa)
        current_fuel_liters -= (km_driven / efficiency)
        
        if curr_date >= date.today():
            break

        current_km += km_driven

        # =====================================================================
        # A. MANUTENZIONE
        # =====================================================================

        # 1. TAGLIANDO LOGICO (ogni ~20.000 km alternati Minore/Maggiore)
        service_interval = random.randint(19_000, 21_000)
        if (current_km - last_service_km) >= service_interval:
            _disable_previous_expiry(db, last_active_ids["Tagliando"])
            next_expiry_km = current_km + 20_000
            workshop = random.choice(WORKSHOPS)
            
            # Logica Progressiva (Alternata)
            service_cycle = current_km // 20000
            if service_cycle % 2 == 1:
                # Tagliando "Minore" (Olio, Filtri)
                cost = round(random.uniform(200.0, 280.0), 2)
                desc = f"Tagliando Minore (Olio motore, Filtro olio/abitacolo) — {workshop}"
            else:
                # Tagliando "Maggiore" (Cinghie, Candele, Freni liquidi)
                cost = round(random.uniform(450.0, 650.0), 2)
                desc = f"Tagliando Maggiore (Olio, Filtri, Candele/Cinghia) — {workshop}"

            new_rec = crud.create_maintenance(
                db, user_id, curr_date, current_km, "Tagliando",
                cost, desc, expiry_km=next_expiry_km, expiry_date=None
            )
            last_active_ids["Tagliando"] = new_rec.id
            last_service_km = current_km
            maint_count += 1
            print(f"   🔧 {desc} @ {current_km} km ({curr_date}) — €{cost:.2f}")

        # 2. CAMBIO GOMME (ogni ~40-50.000 km)
        tire_interval = random.randint(40_000, 52_000)
        if (current_km - last_tires_km) >= tire_interval:
            _disable_previous_expiry(db, last_active_ids["Gomme"])
            next_expiry_km = current_km + 45_000
            # Stagionalità: se fatto in autunno/primavera → gomme stagionali
            season = "invernali" if curr_date.month in (10, 11, 12, 1, 2, 3) else "estive"
            brand = random.choice(["Michelin", "Pirelli", "Bridgestone", "Continental", "Goodyear"])
            cost = round(random.uniform(380.0, 680.0), 2)
            desc = f"Sostituzione 4 gomme {season} {brand} — {random.choice(WORKSHOPS)}"
            new_rec = crud.create_maintenance(
                db, user_id, curr_date, current_km, "Gomme",
                cost, desc, expiry_km=next_expiry_km, expiry_date=None
            )
            last_active_ids["Gomme"] = new_rec.id
            last_tires_km = current_km
            maint_count += 1
            print(f"   🛞  Gomme @ {current_km} km ({curr_date}) — €{cost:.2f}")

        # 3. BOLLO (annuale, febbraio-aprile)
        if curr_date.year > last_tax_year and curr_date.month in (2, 3, 4):
            _disable_previous_expiry(db, last_active_ids["Bollo"])
            next_expiry_date = date(curr_date.year + 1, 1, 31)
            # Costo bollo variabile per KW (simuliamo auto da 85 KW)
            cost = round(random.uniform(195.0, 240.0), 2)
            desc = f"Bollo auto {curr_date.year} — pagato online ACI"
            new_rec = crud.create_maintenance(
                db, user_id, curr_date, current_km, "Bollo",
                cost, desc, expiry_km=None, expiry_date=next_expiry_date
            )
            last_active_ids["Bollo"] = new_rec.id
            last_tax_year = curr_date.year
            maint_count += 1
            print(f"   📋 Bollo {curr_date.year} ({curr_date}) — €{cost:.2f}")

        # 4. REVISIONE (biennale, mesi estivi dispari/pari alternati)
        rev_due_year  = last_service_rev_year + 2
        if curr_date.year >= rev_due_year and curr_date.month in (5, 6, 7) and \
           curr_date.year > last_service_rev_year:
            _disable_previous_expiry(db, last_active_ids["Revisione"])
            next_expiry_date = date(curr_date.year + 2, 6, 30)
            cost = round(random.uniform(72.0, 95.0), 2)
            esito = random.choice(["Esito: FAVOREVOLE", "Esito: FAVOREVOLE — piccola messa a punto sospensioni"])
            desc = f"Revisione periodica ministeriale. {esito}"
            new_rec = crud.create_maintenance(
                db, user_id, curr_date, current_km, "Revisione",
                cost, desc, expiry_km=None, expiry_date=next_expiry_date
            )
            last_active_ids["Revisione"] = new_rec.id
            last_service_rev_year = curr_date.year
            maint_count += 1
            print(f"   🔎 Revisione @ {current_km} km ({curr_date}) — €{cost:.2f}")

        # 5. EVENTI IMPREVISTI (probabilità ~2.5%/evento)
        # a) Batteria
        if random.random() < 0.015:
            cost = round(random.uniform(95.0, 175.0), 2)
            desc = f"Sostituzione batteria — {random.choice(WORKSHOPS)}"
            crud.create_maintenance(db, user_id, curr_date, current_km, "Batteria", cost, desc)
            maint_count += 1
            print(f"   🔋 Batteria ({curr_date}) — €{cost:.2f}")

        # b) Pastiglie freno
        if random.random() < 0.012 and (current_km - last_service_km) > 30_000:
            cost = round(random.uniform(140.0, 260.0), 2)
            desc = f"Sostituzione pastiglie freno ant. + post. — {random.choice(WORKSHOPS)}"
            crud.create_maintenance(db, user_id, curr_date, current_km, "Riparazione", cost, desc)
            maint_count += 1
            print(f"   🛑 Freni ({curr_date}) — €{cost:.2f}")

        # c) Guasto generico occasionale
        if random.random() < 0.008:
            guasto_opts = [
                ("Sostituzione lampadina faro anteriore sinistro", 25.0, 55.0),
                ("Riparazione sistema di climatizzazione — ricarica gas R134a", 80.0, 140.0),
                ("Sostituzione tergicristalli anteriori e posteriori", 35.0, 65.0),
                ("Riparazione sensore parcheggio posteriore", 90.0, 160.0),
                ("Sostituzione cinghia servizi", 180.0, 280.0),
            ]
            desc_g, c_min, c_max = random.choice(guasto_opts)
            cost = round(random.uniform(c_min, c_max), 2)
            crud.create_maintenance(
                db, user_id, curr_date, current_km, "Riparazione",
                cost, f"{desc_g} — {random.choice(WORKSHOPS)}"
            )
            maint_count += 1
            print(f"   ⚠️  Guasto ({curr_date}) — €{cost:.2f}")

        # =====================================================================
        # B. RIFORNIMENTO (Ora basato sul Serbatotio Virtuale)
        # =====================================================================
        price = get_price_with_noise(curr_date)
        
        # Litri mancanti per fare il pieno (clamp a 0 per sicurezza)
        missing_liters = max(0.0, TANK_CAPACITY - current_fuel_liters)

        if in_summer_burst:
            # Vacanza: sempre pieno, sempre in autostrada
            is_full = True
            liters_added = missing_liters
            station = random.choice(["Eni", "Q8", "Esso"])
            notes = "Autostrada"
            
            summer_burst_remaining -= 1
            if summer_burst_remaining <= 0:
                in_summer_burst = False
        else:
            # Logica Routine Ordinaria
            is_full = True
            if not prev_full:
                is_full = random.random() > 0.30  # Più probabile fare il pieno dopo un parziale
            else:
                is_full = random.random() > 0.18
            
            # Rifornimento Parziale
            if not is_full:
                # Mettiamo tra i 15 e i 30 litri, ma senza superare il max cap
                liters_added = min(missing_liters, random.uniform(15.0, 30.0))
            else:
                liters_added = missing_liters
            
            # Scelta della Stazione in base alle Abitudini
            if random.random() < 0.8:
                station = random.choice(ROUTINE_STATIONS)
                note_extra = random.choice(["Vicino ufficio", "Distributore sotto casa", ""])
            else:
                station = random.choice(FUEL_STATIONS)
                note_extra = random.choice(FUEL_NOTES)
                
            notes = f"{station}" + (f" — {note_extra}" if note_extra else "")

        # Aggiorniamo il serbatoio virtuale reale
        current_fuel_liters += liters_added
        total_cost = liters_added * price

        # Crea Record
        crud.create_refueling(
            db, user_id, curr_date, current_km,
            round(price, 3),
            round(total_cost, 2),
            round(liters_added, 2),
            is_full,
            notes
        )
        fuel_count += 1
        prev_full = is_full


    # =========================================================================
    # 4. REMINDERS CON STORICO ESECUZIONI
    # =========================================================================
    print("\n🔔 Creazione Reminders con storico...")

    # Helper per inserire un reminder + N esecuzioni passate simulate
    def _create_reminder_with_history(title, freq_km, freq_days, last_km, last_dt, notes, history_entries):
        """
        history_entries: lista di (date, km) che simulano esecuzioni passate.
        """
        rem = crud.create_reminder(
            db, user_id,
            title=title,
            frequency_km=freq_km,
            frequency_days=freq_days,
            current_km=last_km,
            current_date=last_dt,
            notes=notes
        )
        for (h_date, h_km) in history_entries:
            entry = ReminderHistory(
                reminder_id=rem.id,
                user_id=user_id,
                date_checked=h_date,
                km_checked=h_km,
                notes="Eseguito regolarmente"
            )
            db.add(entry)
        db.commit()
        return rem

    # 1. Pressione pneumatici (ogni 30 gg) — REGOLARE, fatto 12 gg fa
    _create_reminder_with_history(
        title="Pressione Pneumatici",
        freq_km=None, freq_days=30,
        last_km=current_km - 600,
        last_dt=date.today() - timedelta(days=12),
        notes="Controllare a freddo. Pressione consigliata: 2.3 bar ant., 2.5 bar post.",
        history_entries=[
            (date.today() - timedelta(days=12),  current_km - 600),
            (date.today() - timedelta(days=43),  current_km - 2100),
            (date.today() - timedelta(days=74),  current_km - 3600),
            (date.today() - timedelta(days=105), current_km - 5200),
        ]
    )

    # 2. Controllo livello olio (ogni 2.000 km) — SCADUTO (fatto 2.400 km fa)
    _create_reminder_with_history(
        title="Controllo Livello Olio",
        freq_km=2000, freq_days=None,
        last_km=current_km - 2_400,
        last_dt=date.today() - timedelta(days=47),
        notes="Ripristinare tra min e max sull'astina. Olio: 5W-30 LL04.",
        history_entries=[
            (date.today() - timedelta(days=47),  current_km - 2_400),
            (date.today() - timedelta(days=90),  current_km - 4_400),
            (date.today() - timedelta(days=133), current_km - 6_400),
        ]
    )

    # 3. Pulizia filtro abitacolo (ogni 180 gg) — in scadenza tra poco
    _create_reminder_with_history(
        title="Pulizia Filtro Abitacolo",
        freq_km=None, freq_days=180,
        last_km=current_km - 8_000,
        last_dt=date.today() - timedelta(days=162),
        notes="Sostituzione filtro antipolline. Operazione fai-da-te, ~10 minuti.",
        history_entries=[
            (date.today() - timedelta(days=162), current_km - 8_000),
            (date.today() - timedelta(days=342), current_km - 16_500),
        ]
    )

    # 4. Verifica pastiglie freno (ogni 15.000 km)
    _create_reminder_with_history(
        title="Verifica Pastiglie Freno",
        freq_km=15_000, freq_days=None,
        last_km=current_km - 4_200,
        last_dt=date.today() - timedelta(days=80),
        notes="Da fare durante il tagliando o ogni 15.000 km. Spessore minimo: 3 mm.",
        history_entries=[
            (date.today() - timedelta(days=80),  current_km - 4_200),
            (date.today() - timedelta(days=280), current_km - 14_800),
        ]
    )

    # 5. Liquido lavavetri (ogni 60 gg) — OK, fatto 5 gg fa
    _create_reminder_with_history(
        title="Liquido Lavavetri",
        freq_km=None, freq_days=60,
        last_km=current_km - 200,
        last_dt=date.today() - timedelta(days=5),
        notes="Usare soluzione concentrata antigelo in inverno. Non usare acqua del rubinetto.",
        history_entries=[
            (date.today() - timedelta(days=5),   current_km - 200),
            (date.today() - timedelta(days=67),  current_km - 3_200),
            (date.today() - timedelta(days=130), current_km - 6_300),
        ]
    )

    # =========================================================================
    # 5. RIEPILOGO
    # =========================================================================
    print(f"\n{'='*55}")
    print(f"✅ SEEDING COMPLETATO!")
    print(f"   ⛽ Rifornimenti inseriti : {fuel_count}")
    print(f"   🔧 Manutenzioni         : {maint_count}")
    print(f"   🔔 Reminders            : 5 (con storico esecuzioni)")
    print(f"   📍 KM finali simulati   : {current_km:,}")
    print(f"   📅 Periodo coperto      : {start_date} → {date.today()}")
    print(f"{'='*55}\n")

    db.close()


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════╗")
    print("║   FUELPYTRACKER SEEDER v5 — Dati Realistici      ║")
    print("╚══════════════════════════════════════════════════╝\n")
    target_uuid = input("Inserisci il tuo User ID (UUID) da Supabase: ").strip()

    if len(target_uuid) < 10:
        print("❌ UUID non valido (troppo corto).")
    else:
        seed(target_uuid)