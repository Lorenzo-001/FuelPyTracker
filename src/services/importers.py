import pandas as pd
from sqlalchemy.orm import Session
from database import crud
from datetime import datetime

def parse_upload_file(df: pd.DataFrame) -> pd.DataFrame:
    """
    Legge il file raw, normalizza i nomi e prepara i dati ma NON salva nel DB.
    Restituisce un DataFrame pronto per essere mostrato nella Staging Area.
    """
    # Normalizziamo le colonne
    df.columns = [c.lower().strip() for c in df.columns]
    
    clean_data = []
    
    for index, row in df.iterrows():
        raw_date = row.get('data')

        if isinstance(raw_date, str):
                # Prova formati comuni: DD/MM/YYYY o YYYY-MM-DD
                try:
                    d_date = datetime.strptime(raw_date, "%d/%m/%Y").date()
                except ValueError:
                    d_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        else:
                d_date = raw_date.date() # Se è già datetime (da Excel)

            # Parsing Numeri
        d_km = int(row.get('km'))
        d_price = float(str(row.get('prezzo')).replace(',', '.'))
        d_cost = float(str(row.get('costo')).replace(',', '.'))
            
            # Litri: se mancano, li calcoliamo
        if 'litri' in row and pd.notna(row['litri']):
                 d_liters = float(str(row.get('litri')).replace(',', '.'))
        else:
                d_liters = d_cost / d_price

            # Pieno: Default TRUE se manca
        d_full = True
        if 'pieno' in row:
                val = str(row.get('pieno')).lower()
                if val in ['no', 'false', '0', 'n']:
                    d_full = False
        
        # Esempio sintetico (usa il tuo parsing completo):
        try:
            # ... parsing date, km, price ...
            clean_item = {
                "data": d_date, # Oggetto date
                "km": d_km,
                "prezzo": d_price,
                "costo": d_cost,
                "litri": d_liters,
                "pieno": d_full,
                "check": True # Colonna per selezionare se importarlo o no
            }
            clean_data.append(clean_item)
        except Exception:
            continue # O gestisci errore

    return pd.DataFrame(clean_data)

def save_single_row(db, row):
    """Salva una singola riga del DataFrame nel DB."""
    # Ricalcolo litri per sicurezza
    liters = float(row['Litri'])
    if liters <= 0 and float(row['Prezzo']) > 0:
        liters = float(row['Costo']) / float(row['Prezzo'])

    crud.create_refueling(
        db, 
        pd.to_datetime(row['Data']).date(), 
        int(row['Km']), 
        float(row['Prezzo']), 
        float(row['Costo']), 
        liters, 
        bool(row['Pieno']),
        "Import Massivo"
    )