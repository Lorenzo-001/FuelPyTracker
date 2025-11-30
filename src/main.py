from datetime import date
from src.database.core import init_db, get_db
from src.database import crud

def test_insertion():
    print("[INFO] Avvio test inserimento dati...")
    
    # Otteniamo una sessione dal generatore
    db = next(get_db())
    
    try:
        # 1. Creazione di un rifornimento di test
        # Dati simulati: 25 Nov 2025, 100.000 km, 1.75 €/L, 50€ totale, ~28.5L, Pieno SI
        print("[INFO] Tentativo di inserimento nuovo rifornimento...")
        refueling = crud.create_refueling(
            db=db,
            date_obj=date(2025, 11, 25),
            total_km=100000,
            price_per_liter=1.750,
            total_cost=50.00,
            liters=28.57,
            is_full_tank=True,
            notes="Primo inserimento di test"
        )
        print(f"[SUCCESS] Rifornimento inserito. ID generato: {refueling.id}")

        # 2. Lettura dei dati per verifica
        print("[INFO] Lettura dati dal database...")
        records = crud.get_all_refuelings(db)
        
        print(f"[INFO] Trovati {len(records)} record nel database:")
        for record in records:
            # Stampa tecnica dell'oggetto (__repr__)
            print(f" - {record}")

    except Exception as e:
        print(f"[ERROR] Si è verificato un errore durante il test: {e}")
    finally:
        # La chiusura è gestita dal generatore get_db, ma per sicurezza in script raw:
        db.close()

if __name__ == "__main__":
    # Inizializza le tabelle (idempotente: se esistono non fa nulla)
    init_db()
    # Esegue il test
    test_insertion()