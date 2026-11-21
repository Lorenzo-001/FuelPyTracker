"""
Script di ripristino sicuro per l'ambiente di test (Zero-State Demo Reset).
ATTENZIONE: Questo script agisce ESCLUSIVAMENTE sui record associati all'utente demo
(ID: 00000000-0000-4000-8000-000000000001). 
NON tocca né modifica alcun dato appartenente a utenti reali presenti nel database Supabase.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Assicura il caricamento del backend
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.database.core import SessionLocal
from src.database.models import Refueling, Maintenance, Reminder, ReminderHistory, AppSettings
from src.config import DEFAULTS
from src.api.config import DEMO_USER_ID

SAFE_DEMO_USER_ID = "00000000-0000-4000-8000-000000000001"


def reset_demo_data():
    # Verifica di sicurezza assoluta: procedi solo se l'ID è rigorosamente quello demo
    if DEMO_USER_ID != SAFE_DEMO_USER_ID:
        print(f"❌ ERRORE DI SICUREZZA: DEMO_USER_ID configurato è '{DEMO_USER_ID}', diverso da '{SAFE_DEMO_USER_ID}'. Operazione annullata.")
        return False

    db = SessionLocal()
    try:
        print(f"🔒 Avvio pulizia sicura e isolata per l'utente demo: {SAFE_DEMO_USER_ID}...")

        # 1. Pulizia Rifornimenti Demo
        ref_deleted = db.query(Refueling).filter(Refueling.user_id == SAFE_DEMO_USER_ID).delete(synchronize_session=False)
        print(f"   ✓ Rifornimenti demo rimossi: {ref_deleted}")

        # 2. Pulizia Manutenzioni Demo
        maint_deleted = db.query(Maintenance).filter(Maintenance.user_id == SAFE_DEMO_USER_ID).delete(synchronize_session=False)
        print(f"   ✓ Interventi manutenzione demo rimossi: {maint_deleted}")

        # 3. Pulizia Storico Esecuzioni Promemoria Demo (tramite join o ID promemoria demo)
        demo_reminder_ids = [r.id for r in db.query(Reminder.id).filter(Reminder.user_id == SAFE_DEMO_USER_ID).all()]
        history_deleted = 0
        if demo_reminder_ids:
            history_deleted = db.query(ReminderHistory).filter(ReminderHistory.reminder_id.in_(demo_reminder_ids)).delete(synchronize_session=False)
        print(f"   ✓ Storico promemoria demo rimosso: {history_deleted}")

        # 4. Pulizia Promemoria Demo
        rem_deleted = db.query(Reminder).filter(Reminder.user_id == SAFE_DEMO_USER_ID).delete(synchronize_session=False)
        print(f"   ✓ Promemoria demo rimossi: {rem_deleted}")

        # 5. Ripristino Impostazioni Predefinite Demo
        settings = db.query(AppSettings).filter(AppSettings.user_id == SAFE_DEMO_USER_ID).first()
        if not settings:
            settings = AppSettings(user_id=SAFE_DEMO_USER_ID)
            db.add(settings)

        settings.price_fluctuation_cents = 0.15
        settings.max_total_cost = 120.0
        settings.max_accumulated_partial_cost = 80.0
        settings.import_kml_min = 3.0
        settings.import_kml_max = 30.0
        settings.import_kml_error = 50.0
        settings.import_kmd_max = 1000.0
        settings.ocr_add_station_to_notes = True
        settings.ocr_add_liters_to_notes = True
        settings.reminder_types = list(DEFAULTS.SETTINGS.REMINDER_TYPES)
        settings.maintenance_types = list(DEFAULTS.SETTINGS.MAINTENANCE_TYPES)

        db.commit()
        print("   ✓ Impostazioni utente demo ripristinate ai valori predefiniti ufficiali.")
        print("🎉 Reset completato con successo: ambiente demo pronto per il collaudo da zero!\n")
        return True

    except Exception as exc:
        db.rollback()
        print(f"❌ Errore durante il reset dell'utente demo: {exc}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    reset_demo_data()
